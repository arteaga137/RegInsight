from config import config
from scrapers.selenium_scraper import extract_articles_with_selenium
from email_processor.email_fetcher import fetch_emails
from email_processor.content_extractor import extract_content
from summarization.summarizer import summarize_content
from reporting.report_generator import create_word_report_with_analysis, create_excel_report_with_analysis

def main():
    emails_data = fetch_emails(config.EMAIL_USER, config.EMAIL_PASSWORD)
    summaries = summarize_content(emails_data, config.OPENAI_API_KEY)
    
    report_type = input("Enter 'word' for Word report, 'excel' for Excel report, or 'both' for both: ").strip().lower()
    if report_type == "word":
        create_word_report_with_analysis(summaries)
    elif report_type == "excel":
        create_excel_report_with_analysis(summaries)
    elif report_type == "both":
        create_word_report_with_analysis(summaries)
        create_excel_report_with_analysis(summaries)
    else:
        print("Invalid option selected. Please choose 'word', 'excel', or 'both'.")

if __name__ == "__main__":
    main()