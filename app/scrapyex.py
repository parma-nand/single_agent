import scrapy

class NaukriSpider(scrapy.Spider):
    name = "naukri"

    start_urls = [
        "https://www.naukri.com/machine-learning-engineer-or-ai-engineer-or-llm-engineer-or-genai-engineer-jobs-in-pune"
    ]

    def parse(self, response):
        print("STATUS:", response.status)
        print("URL:", response.url)

        with open("naukri.html", "w", encoding="utf-8") as f:
            f.write(response.text)

        print("HTML saved")
        print("Just for Git")