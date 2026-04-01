from gradio_client import Client, handle_file


def call_ai_service(video_url):
    client = Client("https://siyad369-sves-space.hf.space")

    result = client.predict(
        video=handle_file(video_url),
        api_name="/analyze_video"
    )

    return result

# def call_ai_service(video_url):
#     try:
#         # Try repo name first
#         client = Client("siyad369/sves_space")
#     except:
#         # Fallback to URL
#         client = Client("https://siyad369-sves-space.hf.space")
#
#     result = client.predict(
#         video=handle_file(video_url),
#         api_name="/analyze_video"
#     )
#
#     return result