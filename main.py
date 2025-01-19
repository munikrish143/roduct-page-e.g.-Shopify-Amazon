from fastapi import FastAPI, Query, HTTPException
from playwright.async_api import async_playwright
import openai
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Ensure API key is set
if not OPENAI_API_KEY:
    raise ValueError("Missing OPENAI_API_KEY in environment variables")

openai.api_key = OPENAI_API_KEY

app = FastAPI()

async def get_dynamic_selectors(page_content: str) -> dict:
    """Use to dynamically extract review-related CSS selectors."""
    prompt = f"""
    Extract CSS selectors for product reviews from the following HTML content:
    {page_content[:5000]}  # Limit to avoid token overflow
    
    Return the result in JSON format with keys: title, body, rating, reviewer, next_page.
    Example:
    {{
      "title": ".review-title",
      "body": ".review-body",
      "rating": ".review-rating",
      "reviewer": ".reviewer-name",
      "next_page": ".next-button"
    }}
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "Extract review CSS selectors."},
                      {"role": "user", "content": prompt}],
            max_tokens=500
        )
        selectors = json.loads(response["choices"][0]["message"]["content"])
        return selectors
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in OpenAI request: {str(e)}")

async def extract_reviews(url: str):
    """Scrape reviews from a product page dynamically."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # Headless browser mode
        page = await browser.new_page()
        await page.goto(url, timeout=60000)
        await page.wait_for_timeout(3000)  # Allow time for content to load

        html_content = await page.content()
        selectors = await get_dynamic_selectors(html_content)

        reviews = []
        while True:
            titles = await page.evaluate(f"Array.from(document.querySelectorAll('{selectors['title']}')).map(e => e.innerText)")
            bodies = await page.evaluate(f"Array.from(document.querySelectorAll('{selectors['body']}')).map(e => e.innerText)")
            ratings = await page.evaluate(f"Array.from(document.querySelectorAll('{selectors['rating']}')).map(e => e.innerText)")
            reviewers = await page.evaluate(f"Array.from(document.querySelectorAll('{selectors['reviewer']}')).map(e => e.innerText)")

            for i in range(len(titles)):
                reviews.append({
                    "title": titles[i],
                    "body": bodies[i],
                    "rating": ratings[i],
                    "reviewer": reviewers[i]
                })

            next_page_button = await page.query_selector(selectors.get("next_page"))
            if next_page_button:
                await next_page_button.click()
                await page.wait_for_timeout(3000)  # Wait for new reviews to load
            else:
                break

        await browser.close()
        return {"reviews_count": len(reviews), "reviews": reviews}

@app.get("/api/reviews")
async def get_reviews(page: str = Query(..., description="URL of the product page")):
    """API Endpoint to fetch reviews dynamically."""
    try:
        data = await extract_reviews(page)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching reviews: {str(e)}")
