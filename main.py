import json
import requests
import time
import openai

def load_config(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def authenticate(url, credentials):
    response = requests.post(url, json=credentials)
    if response.status_code == 200 or response.status_code == 201:
        data = response.json()
        return data.get("accessToken", None)
    else:
        print("Failed to authenticate. Status code:", response.status_code)
        return None

def send_graphql_request(url, body, headers):
    response = requests.post(url, json=body, headers=headers)
    return response

def generate_article_topics_and_contents(category_name, location_name):
    def get_article_topics(category_name, location_name):
        prompt = f"Suggest 5 article topics related to {category_name} in {location_name}\nI only need article topics"
        prompt_explain = "Please show me only article topics, and I don't want any explanation and index of article topics"
        prompt = prompt + prompt_explain

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        suggested_topics = completion.choices[0].message['content']
        topic_list = [topic.split(". ")[1] for topic in suggested_topics.split("\n")]

        return topic_list

    def generate_article_content(topic):
        prompt = f"Write the detailed short article without title part and conclusion part on - {topic}"
        prompt_explain = "Please write shortly, it should be up to 7 sentences"
        prompt = prompt + prompt_explain

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        article_content = completion.choices[0].message['content']

        return article_content

    article_topics = get_article_topics(category_name, location_name)

    article_dict = {}
    for topic in article_topics:
        article_content = generate_article_content(topic)
        article_dict[topic] = article_content

    return article_dict
def generate_guide_topics_and_contents(category_name, location_name):
    def get_guide_topics(category_name, location_name):
        prompt = f"Suggest 5 guide article related to {category_name} in {location_name}\nI only need guide article topics and it should contain 'guide' word"
        prompt_explain = "Please show me only guide article topics, and I don't want any explanation and index of article topics"
        prompt = prompt + prompt_explain

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        suggested_topics = completion.choices[0].message['content']
        topic_list = [topic.split(". ")[1] for topic in suggested_topics.split("\n")]

        return topic_list

    def generate_guide_content(topic):
        prompt = f"Write the detailed short guide article without title part and conclusion part on - {topic}"
        prompt_explain = "Please write shortly, it should be up to 7 sentences"
        prompt = prompt + prompt_explain

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        article_content = completion.choices[0].message['content']

        return article_content

    guide_topics = get_guide_topics(category_name, location_name)

    guide_dict = {}
    for topic in guide_topics:
        guide_content = generate_guide_content(topic)
        guide_dict[topic] = guide_content

    return guide_dict
def generate_faq(category_name, location_name):
    # Function to get FAQ questions
    def get_faq_questions(category_name, location_name):
        # Construct the prompt
        prompt = f"Suggest 5 FAQ questions related to {category_name} in {location_name}\nI only need FAQ questions"
        prompt_explain = "Please show me only FAQ questions, and I don't want any explanation or index of questions"
        prompt = prompt + prompt_explain

        # Create a chatbot using ChatCompletion.create() function
        completion = openai.ChatCompletion.create(
            # Use GPT 3.5 as the language model
            model="gpt-3.5-turbo",
            # Pre-define conversation messages for the possible roles
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        # Extract the suggested questions from the completion
        suggested_questions = completion.choices[0].message['content']

        # Split the questions into a list and remove the index
        question_list = [question.split(". ")[1] for question in suggested_questions.split("\n")]

        return question_list

    # Function to generate FAQ answers
    def generate_faq_answers(question):
        # Construct the prompt
        prompt = f"Write the answer to the FAQ question: '{question}'"
        prompt_explain = "Please keep the answer concise, up to 7 sentences."
        prompt = prompt + prompt_explain

        # Create a chatbot using ChatCompletion.create() function
        completion = openai.ChatCompletion.create(
            # Use GPT 3.5 as the language model
            model="gpt-3.5-turbo",
            # Pre-define conversation messages for the possible roles
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        # Extract the FAQ answer from the completion
        faq_answer = completion.choices[0].message['content']

        return faq_answer

    # Get the FAQ questions
    faq_questions = get_faq_questions(category_name, location_name)

    # Generate answers for the FAQ questions
    faq_dict = {}
    for question in faq_questions:
        faq_answer = generate_faq_answers(question)
        faq_dict[question] = faq_answer

    return faq_dict

# Constants
USER_JSON_PATH = 'user.json'
CATEGORY_JSON_PATH = 'category.json'
LOCATION_JSON_PATH = 'location.json'
AUTH_URL = "https://api.closebynearme.com/auth/login"
GRAPHQL_URL = "https://api.closebynearme.com/graphql"

# Load user credentials
config = load_config(USER_JSON_PATH)
usermail = config.get('usermail', '')
password = config.get('password', '')
openai_key = config.get('openai-key', '')
openai.api_key = openai_key

# Authenticate user
credentials = {"email": usermail, "password": password, "rememberMe": True}
access_token = authenticate(AUTH_URL, credentials)

if access_token:
    headers = {"Authorization": f"Bearer {access_token}"}

    # Load category and location data
    category_data = load_config(CATEGORY_JSON_PATH)
    location_data = load_config(LOCATION_JSON_PATH)

    # Send requests for articles and FAQs
    for category_name, category_id in category_data.items():
        for location_name, location_id in location_data.items():
            articles = generate_article_topics_and_contents(category_name, location_name)
            for title, content in articles.items():
                # Construct GraphQL request body for article
                article_body = {
                    "operationName": "CreateArticle",
                    "variables": {
                        "input": {
                            "categoryId": category_id,
                            "categoryName": category_name,
                            "description": "test" + content,
                            "locationId": location_id,
                            "locationName": location_name,
                            "title": "test" + title.replace('"', ''),
                            "image": "",
                            "type": "DEFAULT"
                        }
                    },
                    "query": "mutation CreateArticle($input: CreateArticleInput!) {\n  createArticle(input: $input)\n}"
                }
                response_article = send_graphql_request(GRAPHQL_URL, article_body, headers)
                if response_article.status_code == 200:
                    print("Request for article successful!")
                    print("Response for article:")
                    print(response_article.json())
                else:
                    print("Request for article failed.")
            
            guides = generate_guide_topics_and_contents(category_name, location_name)
            for title, content in guides.items():
                # Construct GraphQL request body for article
                guide_body = {
                    "operationName": "CreateArticle",
                    "variables": {
                        "input": {
                            "categoryId": category_id,
                            "categoryName": category_name,
                            "description": "test" + content,
                            "locationId": location_id,
                            "locationName": location_name,
                            "title": "test" + title,
                            "image": "",
                            "type": "GUIDE"
                        }
                    },
                    "query": "mutation CreateArticle($input: CreateArticleInput!) {\n  createArticle(input: $input)\n}"
                }
                response_guide = send_graphql_request(GRAPHQL_URL, guide_body, headers)
                if response_guide.status_code == 200:
                    print("Request for guide successful!")
                    print("Response for guide:")
                    print(response_guide.json())
                else:
                    print("Request for guide failed.")

            faqs = generate_faq(category_name, location_name)
            for question, answer in faqs.items():
                # Construct GraphQL request body for FAQ
                faq_body = {
                    "operationName": "CreateFaq",
                    "variables": {
                        "input": {
                            "answer": "test" + answer,
                            "question": "test" + question,
                            "categoryId": category_id,
                            "categoryName": category_name,
                            "locationId": location_id,
                            "locationName": location_name
                        }
                    },
                    "query": "mutation CreateFaq($input: CreateFaqInput!) {\n createFaq(input: $input)\n }"
                }
                response_faq = send_graphql_request(GRAPHQL_URL, faq_body, headers)
                if response_faq.status_code == 200:
                    print("Request for FAQ successful!")
                    print("Response for FAQ:")
                    print(response_faq.json())
                else:
                    print("Request for FAQ failed.")

            time.sleep(5)  # Delay before sending the next requests to avoid rate limiting
