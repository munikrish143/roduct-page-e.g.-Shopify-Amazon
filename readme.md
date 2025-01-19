# Product Review Scraper API

This project provides an API to dynamically extract product reviews from any given URL (e.g., Shopify, Amazon). It uses Playwright for scraping and OpenAI's GPT-4 model to identify the CSS selectors for reviews and pagination dynamically.

## Features

- Extract product reviews (title, body, rating, reviewer) from any product page.
- Handle pagination to scrape reviews across multiple pages.
- Dynamically identify the CSS selectors for reviews and pagination.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/munikrish143/roduct-page-e.g.-Shopify-Amazon/upload/main
   cd your-product-page-e.g.-Shopify-Amazon
   ```

2. Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up the `.env` file with your OpenAI API key:

   ```
   OPENAI_API_KEY=your-openai-api-key
   ```

5. Install Playwright browsers:
   ```bash
   python -m playwright install
   ```

## Running the Application

To start the FastAPI server, run:

```bash
uvicorn main:app --reload
```
