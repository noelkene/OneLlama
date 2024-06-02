
import os
import streamlit as st
from google.cloud import storage
import subprocess


from vertexai.preview.generative_models import (Content,
                                                GenerationConfig,
                                                GenerativeModel,
                                                GenerationResponse,
                                                Image,
                                                HarmCategory,
                                                HarmBlockThreshold,
                                                Part)
import vertexai
PROJECT_ID = os.environ.get('GCP_PROJECT') #Your Google Cloud Project ID
LOCATION = os.environ.get('GCP_REGION')   #Your Google Cloud Project Region
vertexai.init(project=PROJECT_ID, location=LOCATION)

@st.cache_resource
def load_models():
    text_model_pro = GenerativeModel("gemini-pro")
    multimodal_model_pro = GenerativeModel("gemini-pro-vision")
    return text_model_pro, multimodal_model_pro

def get_gemini_pro_text_response( model, prompt_input,
                                  generation_config: GenerationConfig,
                                  stream=True):


    safety_settings={
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }


    responses = model.generate_content(prompt_input,
                                       generation_config = generation_config,
                                       safety_settings=safety_settings,
                                       stream=True)

    final_response = []
    for response in responses:
        try:
            # st.write(response.text)
            final_response.append(response.text)
        except IndexError:
            # st.write(response)
            final_response.append("")
            continue
    return " ".join(final_response)


def get_gemini_pro_vision_response(model, prompt_list, generation_config={},  stream=True):
    generation_config = {'temperature': 0.1,
                         'max_output_tokens': 2048
                         }
    responses = model.generate_content(prompt_list,
                                       generation_config = generation_config,stream=True)
    final_response = []
    for response in responses:
        try:
            final_response.append(response.text)
        except IndexError:
            pass
    return("".join(final_response))

def save_html(html_content, filename):
    if not os.path.exists("webpages"):
        os.makedirs("webpages")
    with open(os.path.join("webpages", filename), 'w') as f:
        f.write(html_content)

    subprocess.run(['gsutil cp ./webpages/* gs://onellama_bucket/'])

#       upload_to_gcs(filename, "vera_bucket_onellama")
#    copy_tree_to_gcs("./webpages", "vera_bucket_onellama", gcs_prefix='')

def upload_to_gcs(filename, bucket_name):
    bucket = storage.Client().bucket(bucket_name)
    blob = bucket.blob(filename)
    fullpath = os.path.join("./webpages", filename)
    print(f'{fullpath}')
    blob.upload_from_filename(fullpath)
    print(f'Uploaded {filename} to gs://{bucket_name}/{filename}')
    #subprocess.run([f'gsutil cp * gs://{bucket_name}/'])
    subprocess.run(['gsutil', 'cp', './webpages/*', f'gs://{bucket_name}/'])


#def upload_to_gcs(filename, bucket_name):
#    subprocess.run(['gsutil cp ./webpages/{filename}', f'gs://{bucket_name}/{filename}'])
#    subprocess.run(['gsutil', 'cp', fullpath, f'gs://{bucket_name}/{filename}'])


def display_webpages():
    pages = [f for f in os.listdir("webpages") if f.endswith(".html")]
    if pages:
        for page in pages:
            page_path = os.path.join("https://storage.mtls.cloud.google.com/onellama_bucket/", page)
            # Construct a link that opens in a new tab using target="_blank"
            link = f'<a href="{page_path}" target="_blank">{page}</a>'
            st.markdown(link, unsafe_allow_html=True)
    else:
        st.write("No webpages created yet.")



def copy_tree_to_gcs(local_dir, bucket_name, gcs_prefix=None):
    for root, _, files in os.walk(local_dir):
        for file in files:
            local_path = os.path.join(root, file)
            rel_path = os.path.relpath(local_path, local_dir)
            blob_name = os.path.join(gcs_prefix, rel_path) if gcs_prefix else rel_path
            blob = bucket.blob(blob_name)
            blob.upload_from_filename(local_path)
            print(f'Uploaded {local_path} to gs://{bucket_name}/{blob_name}')



st.header("Technology powered by One Llama", divider="rainbow")
text_model_pro, multimodal_model_pro = load_models()

#tab1 = st.tabs(["Creating webpage content for One Llama"])
#tab1, tab2, tab3 = st.tabs(["Chapter summary","Consistency Check", "Consistency Check with PDFs"])
tab1, tab2 = st.tabs(["Creating content for One Llama website", "Single query search"])



with tab1:
    st.write("this tool is designed to generate web pages associated with One Llama")
    st.subheader("Based on the text inserted below, we will generate a webpage of content")

    # Story premise
    input_topic = st.text_input("Enter topic from which to generate content \n\n",key="input_topic",value="Input topic e.g. Machu Picchu")


    temperature = 0.30


    max_output_tokens = 6048

    prompt = f""" You are an Expert tour guide and historian professor involved in writing articles to attract people to Peru. Your job is to create a landing page One Llama tours company that promotes the given TOPIC. The landing page has three sections. Headline, Abstract and Takeaway Bullets."


Headline: factual and based on the TOPIC that captures the key points in less than 100 characters. The headline should be attention-grabbing, concise, and should clearly convey the reason to visit.


Make sure it encourages visitors to explore more of the page.


Abstract: factual summary of TOPIC in less than 500 characters. Ensure that the text is engaging and informative. Do not use any bullet points."


Takeaway Bullets: 3 takeaways that tell visitors what are the most important aspects of the TOPIC in a concise and visually appealing manner .The goal is to reinforce the value proposition and encourage visitors to take action. "


Do not give too many details in each takeaway and keep it short. Do not give more than 5 takeaways.





 All content returned should be factual and accurate and should only be in the english language.

    TOPIC: {input_topic} 
    """
    # config = GenerationConfig(
    #     temperature=temperature,
    #     candidate_count=1,
    #     max_output_tokens=max_output_tokens,
    # )

    config = {
        "temperature": 0.8,
        "max_output_tokens": 6048,
    }

    generate_t2t = st.button("Generate One Llama content", key="generate_t2t")
    if generate_t2t and prompt:
        # st.write(prompt)

        with st.spinner("Generating your One Llama content. Sit back and dream of Peru..."):
            first_tab1, first_tab2 = st.tabs(["One llama content", "Prompt"])
            with first_tab1:
                response_html_temp = get_gemini_pro_text_response(
                    text_model_pro,
                    prompt,
                    generation_config=config,
                )
                prompt_wrap_html =  f""" Wrap the following TEXT in an HTML template. Include headers, paragraphs and bullets
    TEXT: {response_html_temp} 
    """
                response_html = get_gemini_pro_text_response(
                    text_model_pro,
                    prompt_wrap_html,
                    generation_config=config,
                )




            if response_html:
                st.write("Your new content:")
                st.write(response_html)
            with first_tab2:
                st.text(prompt)


            new_html = response_html
            filename = input_topic + ".html"
            if filename:
                save_html(new_html, filename)
    if st.button("View Webpages"):
        display_webpages()





with tab2:
    st.write("This is a search engine for all things Peru")
    st.subheader("Based on your input we will help guide your trip to Peru")

    # Story premise
    question = st.text_input("Enter question \n\n",key="question",value="What is the best time of year to visit Machu Picchu")


    temperature = 0.30


    max_output_tokens = 6048

    prompt_question = f""" You are an Expert tour guide and historian professor. Your job is to answer users QUESTION as thoroughly and accuratley as possible
Elaborate on your answer.
Give the user options

 All content returned should be factual and accurate and should only be in the english language.

    QUESTION: {question} 
    """
    # config = GenerationConfig(
    #     temperature=temperature,
    #     candidate_count=1,
    #     max_output_tokens=max_output_tokens,
    # )

    config = {
        "temperature": 0.8,
        "max_output_tokens": 6048,
    }

    generate_tab2button = st.button("Get an amazing OneLlama answer", key="generate_tab2button")
    if generate_tab2button and prompt_question:
        # st.write(prompt)
        with st.spinner("One Llama is thinking about the best response"):
            second_tab1, second_tab2 = st.tabs(["One Llama response", "Prompt"])
            with second_tab1:
                question_response = get_gemini_pro_text_response(
                    text_model_pro,
                    prompt_question,
                    generation_config=config,
                )
                if question_response:
                    st.write("And here is your answer:")
                    st.write(question_response)
            with second_tab2:
                st.text(prompt_question)






