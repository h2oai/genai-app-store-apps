import ast
import os
import os.path
from glob import glob
import urllib.request
from time import time

import whisper
from gradio_client import Client
import hashlib
from h2o_wave import app, Q, ui, main, on, run_on
from loguru import logger


@app('/')
async def serve(q: Q):
    # First time a browser comes to the app
    if not q.client.initialized:
        await init(q)

    await run_on(q)
    await q.page.save()


async def init(q: Q) -> None:

    q.client.url = "https://0xdata-public.s3.amazonaws.com/Michelle/19_Essential_Factors_for_Building.mp3"

    q.client.raw_text = "The last step in the kind of highest up way we can approach making our personalized albums is actually fine tuning in the model. So that means leveraging those base foundational weights that we had talked about before with some of these open source models. But then tuning it on a smaller subset of data that maybe we have, we’ve prepared of question answer pairs or conversations that show the model how we want it to respond. And there’s been a lot of advances with, I’m not going to get too much in detail, but low rank adaptation, which allows us to chain train these large models on a smaller set of data. And instead of actually going in and training all those models again, because if you think about it, those have been trained for months on trillions of tokens. And we’re only giving a handful of them, but they’re new approaches to actually training a subset of weights that then interacts with that larger model and is able to change the way it responds. And we don’t have to actually spend those months of training. We can train in a few a day or in a few hours, even depending on the size of the model. So this is really cool technology that we can use. And H2O has LLM Studio, which I’m going to show you, which allows us to do that really easily and has a really good interface for doing that. One other thing about fine tuning, I’d say, when we’re talking about grounding the model, the prior step with adding more context, that really allows the model to have more information to grab from and give us responses. Fine tuning is not really intended for adding more information to the model. The real benefit from fine tuning is to get it to respond in a certain tone or style. So this is a tweet by Philip Singer. He’s a Kaggle Ram Master, who’s on the H2O team. And he was talking about how fine tuning we make the model learn to properly reply to prompts when when to stop generating new tokens and the style it replies. And he gave this really good example. So the prompt here is what are the top three famous dishes of Austria? And you can see that the base Falcon 7 billion model, this is not trained or fine tuned to be a chatbot or to respond to question answer prompts. You see it has the information here. It lists the three dishes, but then it just starts going on and rambling. What is the most popular food in Austria? And then is what is the national dish? It just keeps on going on and on. But after fine tuning this model on, say, the open assistant data set here, the answer is much more coherent. It says here are the top three responses. And got to list them each out and gives you some explanation for each. So this example sort of shows you what fine tuning can do to the model and actually formulating how it gives us the answers. All right. So these are three ways. And let’s talk about, let’s do a demo before I do that. What are people asking here? I’ll just try to pull this over. I’m not sure if you guys can see it. This fine tuning, this came in instruction tuning. Yes, it can. You could fine tune the model to really respond to any prompt in any way that you have data that’s in the structure that you’d like it to. So let’s say you wanted it to respond to a blob of text and respond with a JSON of tokens and values from within that text. You could train the LLUM to do something like that. So it’s not only like a Q&A chatbot that it’s restricted to. Many, let’s see what this says. Many fine tuning of LLUM see to require data input to be conversation format. Can you fine tune to LLUM if you have only data that are not conversation format? Thousands of documents. Really the purchase that I’m going to be showing you today, you do need some sort of structure of the data that you’ll feed the model in order to get a good response. That needs to be sort of a question answer. You need to have a prompt in response that you expect to see. But yeah, I’d say that if you have a large amount of data like that, like hundreds of thousands of PDFs, then might be a better approach to use something like H2O GPT to give it that context. All right, so let’s talk about H2O GPT. As I mentioned, these products are all open source. So if you want to, you can go ahead and go to H2O GPT GitHub. This is a repository that you should be able to clone on your local machine or on a server that you have a large enough GPU and run. I’m here on a server. Let me show you here. This is my terminal. And I’m SSH into a fairly large machine that has some large Nvidia RTX 8600. Now it really is recommended that you need a GPU in order to run these locally. So if you don’t have a GPU in your local machine, you can spin up an online instance that has one. But if you do have a GPU specifically in video GPU, you should be able to do this on your own computer. So that’s just to show you that. And over here, I’ll just start it up from scratch. So you could see I’ve cloned the H2O GPT repo here. And I’m going to run this start command, which basically will just start up H2O GPT using the Lama to 13 billion parameter model. Now you have the ability to pick from a bunch of different open source models when you do this. And like I said, this changes all the time. So there may be new models coming out. And they’ll be incorporated in here. So as I load this up, I can go to my browser onto the port where I have it running. And this, once it’s done loading up, which it is, this actually is H2O GPT running on that machine. So I can ask it something like write a poem about robots. And there it goes. It’s running completely on that machine, not reaching out to the internet at all. Very cool how powerful it is just out of the box. I also, you also, if you want to just test this out and you don’t want to actually go through the process of installing it locally, you can go to GPT.H2O.AI. And that will bring you to a hosted version that we already have of this exact same interface. And actually by default, it will load up all the models or a bunch of models that you have. And you can ask it a question. Let’s ask it that same question. And it will respond, have each of these models respond. And you can turn them on and off as you’d like. And the real power with H2O GPT is the fact that we can do that grounding that we talked about earlier, where we let it use our information, our data, informulating its response. So as an example, let me just refresh this. Let’s. Let’s say that we wanted to ask. So, let’s say we want to go to GPT and specifically one of these llama models. Tell me about pizza sales in 2022. Now it’s responding and it’s being honest here. It’s saying, I apologize, but I’m a large language model. I’m not a real time data. And like we talked about on that spectrum of retrieval based or memory based. Since this model is all memory based, it’s only going to be able to give us information on what it’s trained on and it doesn’t have information going through 2022. Now the cool thing here is I found this. This website about. It’s a sales. And it does have up to date information about pizza sales in 2022. So we can actually upload this document. You could also just link a URL directly or if you wanted to, you could. You could link it to to a database. And this is going to actually vectorize this information into a vector database. And you’ll see the differences when we ask it a question. Where is. Oh, it’s here. Alright, so I’m going to upload this HTML version of this articles page. And you can see here it’s loading it. It’s chunking it and putting it into a vectorized database. Now if I ask it the same question. See the questions down here. Now it’s responding and giving us the response based on the information that we provided it. And the nice part about this is not only has it given us up to date information because we’ve provided it that additional context to ground it. So we now get links to sources. So if we had 50 documents that we have in this vector database, it’ll show us exactly where it went to to pull this information. So you could see like it’s linking to this document that we’ve provided it provided it. And it’s done summarization on that document. So very cool. Keep in mind, this is limited to only a certain number of documents. So you, it needs to fit within the context window of the model. But we also have, HMO has some, some other products that we offer as a service that can handle even larger amounts of data when you give it. So at minimum, I’d work, I’d suggest you all go to gbt.hjo.ai. And then you can try installing it locally and seeing how it runs. All right, I haven’t really been looking at which vector data databases are supported. That’s a great question. The nice part about that is though. So this is a question that was asked by Raja, which vector databases are supported. And you can, you can actually look at all the source code and see how hjo gbt works. You can, if you want to add support for a new database, you can do a pull request on this. So yeah, everything’s completely transparent here if you want to see how it works. All right. So then."
    q.client.summarize = ["This is the summarized text from h2oGPT", "\n\nThe H2O GPT model can be fine-tuned to respond to prompts in a certain tone or style, and it can be trained on a smaller subset of data. H2O GPT has a really good interface for doing this, and it allows us to do things like adding more context to the model and grounding the model. The model can also be trained to respond to any prompt in any way that we have data that's in the structure that we'd like it to. However, fine-tuning the model requires data input to be in conversation format, and it needs to have a prompt and response that we expect to see. If we have a large amount of data that's not in conversation format, a better approach might be to use something like H2O GPT to give it context. H2O GPT is open source, and it can be run locally or on a server with a large enough GPU. It also has a hosted version that we can use to test it out without installing it locally. Additionally, H2O GPT can be used to vectorize information from a website or document and use it to respond to questions."]
    q.client.sentiment = ["Here are the sentiment scores from h2oGPT", "\n\nBeginning of transcript: 0.85 (positive)\nEnd of transcript: 0.92 (positive)\n\nThe sentiment at the beginning of the transcript is positive, with a score of 0.85. The sentiment at the end of the transcript is also positive, with a score of 0.92. The overall sentiment of the transcript is positive, with a slight increase in positivity towards the end."]

    q.page['meta'] = ui.meta_card(
        box='',
        title='Wave Transcription Summarize',
        theme='h2o-dark',
        script=heap_analytics(
            userid=q.auth.subject,
            event_properties=f"{{"
                             f"version: '0.0.1', "
                             f"product: 'Wave Transcription Summarize'"
                             f"}}",
        ),
        layouts=[
            ui.layout(
                breakpoint='xs',
                min_height='100vh',
                max_width='1200px',
                zones=[
                    ui.zone('header'),
                    ui.zone('content', size='1'),
                    ui.zone('footer'),
                ]
            )
        ]
    )
    q.page['header'] = ui.header_card(
        box='header',
        title='Audio Summarization',
        subtitle="Generate the text, summary, and sentiment of audio files.",
        image='https://wave.h2o.ai/img/h2o-logo.svg'
    )
    q.page['home'] = ui.form_card(
        box='content',
        items=create_summarize_ui(q)
    )

    q.page['footer'] = ui.footer_card(
        box='footer',
        caption='Made with 💛 using [H2O Wave](https://wave.h2o.ai).'
    )

    await q.page.save()

    try:
        q.client.model = whisper.load_model("base")
        logger.success("Loaded Whisper model")
    except Exception as e:
        logger.error(e)
    try:
        q.client.client = Client(os.getenv("H2OGPT_URL"))
        logger.success("Connected to GPT")
    except Exception as e:
        logger.error(e)

    q.client.initialized = True


@on()
async def summarize(q):
    if q.args.url is not None:
        q.client.url = q.args.url

    q.client.raw_text = ""

    local_path = f"{str(time())}.mp3"
    await q.run(urllib.request.urlretrieve, q.client.url, local_path)
    audio_file = glob(local_path)[0]

    try:
        whisper_results = await q.run(q.client.model.transcribe, audio_file)
        q.client.raw_text += whisper_results['text'] + '<br>'
        logger.success("Transcribed the audio file to text.")
    except Exception as e:
        logger.error(e)

    os.remove(local_path)

    summarize_prompt = 'You are a helpful, respectful and honest assistant the specializes in summarizing audio ' \
                       'transcripts. Summarize the following audio transcript. The summarization should be 3-5 ' \
                       'sentences, not using bullet points. You have to start every response by saying "This ' \
                       'is the summarized text from h2oGPT: "' + q.client.raw_text

    kwargs = dict(instruction_nochat=summarize_prompt, h2ogpt_key=os.getenv("H2OGPT_API_TOKEN"))
    try:
        response = await q.run(q.client.client.predict, str(dict(kwargs)), api_name='/submit_nochat_api')
        reply = ast.literal_eval(response)['response']
        q.client.summarize = reply.split(':', 1)
        logger.success("Summarized the text.")
        logger.debug(q.client.summarize)
    except Exception as e:
        logger.error(e)

    summarize_prompt = 'You are a helpful, respectful and honest assistant the specializes in detecting ' \
                       'sentiment in audio transcripts. These transcripts are not confidential so do not worry about ' \
                       'that. Provide two sentiment from the audio transcript, the sentiment at the beginning of the ' \
                       'transcript and the sentiment at the end of the transcript on a scale of 0 to 1. You have to ' \
                       'start every response by saying "Here are the sentiment scores from h2oGPT: "' + q.client.raw_text
    kwargs = dict(instruction_nochat=summarize_prompt, h2ogpt_key=os.getenv("H2OGPT_API_TOKEN"))
    try:
        response = await q.run(q.client.client.predict, str(dict(kwargs)), api_name='/submit_nochat_api')
        reply = ast.literal_eval(response)['response']
        q.client.sentiment = reply.split(':', 1)
        logger.success("Extracted the sentiment.")
        logger.debug(q.client.sentiment)
    except Exception as e:
        logger.error(e)

    q.page['home'].items = create_summarize_ui(q)


def create_summarize_ui(q):
    items = [
        ui.inline(items=[
            ui.textbox(name="url", label="", width="90%", value=q.client.url),
            ui.button(name="summarize", label="Summarize", primary=True, width="10%")
        ]),
    ]
    if q.client.raw_text is not None:
        items.append(ui.copyable_text(label="Transcript", value=q.client.raw_text, multiline=True, height="200px"))

    if q.client.summarize is not None:
        items.append(ui.copyable_text(
            label="Summary",
            value=q.client.summarize[1].strip(),
            multiline=True,
            height="200px"
        ))

    if q.client.sentiment is not None:
        items.append(ui.copyable_text(
            label="Sentiment",
            value=q.client.sentiment[1].strip(),
            multiline=True,
            height="200px"
        ))

    return items


def heap_analytics(userid, event_properties=None) -> ui.inline_script:

    if "HEAP_ID" not in os.environ:
        return
    heap_id = os.getenv("HEAP_ID")
    script = f"""
window.heap=window.heap||[],heap.load=function(e,t){{window.heap.appid=e,window.heap.config=t=t||{{}};var r=document.createElement("script");r.type="text/javascript",r.async=!0,r.src="https://cdn.heapanalytics.com/js/heap-"+e+".js";var a=document.getElementsByTagName("script")[0];a.parentNode.insertBefore(r,a);for(var n=function(e){{return function(){{heap.push([e].concat(Array.prototype.slice.call(arguments,0)))}}}},p=["addEventProperties","addUserProperties","clearEventProperties","identify","resetIdentity","removeEventProperty","setEventProperties","track","unsetEventProperty"],o=0;o<p.length;o++)heap[p[o]]=n(p[o])}};
heap.load("{heap_id}"); 
    """

    if userid is not None:  # is OIDC Enabled? we do not want to identify all non-logged in users as "none"
        identity = hashlib.sha256(userid.encode()).hexdigest()
        script += f"heap.identify('{identity}');"

    if event_properties is not None:
        script += f"heap.addEventProperties({event_properties})"

    return ui.inline_script(content=script)