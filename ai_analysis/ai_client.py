from gradio_client import Client, handle_file


def call_ai_service(video_url):
    client = Client("siyad369/sves_space")

    result = client.predict(
        video=handle_file(video_url),
        api_name="/analyze_video"
    )

    return result