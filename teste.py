from modules.services.recovery import RecoveryService


recovery = RecoveryService()

videos = recovery.encontrar_videos()

print(
    "\n"
    + "=" * 60
)

print(
    f"Total recuperado: {len(videos)}"
)

for video in videos:

    print(
        "\n"
        + "=" * 60
    )

    print(video)

    print(
        f"Caminho: {video.caminho_download}"
    )

    print(
        f"Status: {video.status}"
    )