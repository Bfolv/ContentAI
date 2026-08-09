from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


ROOT_DIR = Path(__file__).resolve().parents[2]


class UploadService:

    SCOPES = [
        "https://www.googleapis.com/auth/youtube.upload"
    ]

    def __init__(self):

        self.credentials = None
        self.youtube = None

        self.credentials_dir = (
            ROOT_DIR /
            "credentials" /
            "youtube"
        )

        self.client_secret = (
            self.credentials_dir /
            "client_secret.json"
        )

        self.token = (
            self.credentials_dir /
            "token.json"
        )

    def autenticar(self):
        """
        Realiza login OAuth.

        Na primeira execução abrirá o navegador.

        Depois reutilizará o token salvo.
        """

        if self.token.exists():

            self.credentials = (
                Credentials.from_authorized_user_file(
                    self.token,
                    self.SCOPES
                )
            )

        if (
            not self.credentials
            or
            not self.credentials.valid
        ):

            if (
                self.credentials
                and
                self.credentials.expired
                and
                self.credentials.refresh_token
            ):

                self.credentials.refresh(Request())

            else:

                flow = (
                    InstalledAppFlow
                    .from_client_secrets_file(
                        self.client_secret,
                        self.SCOPES
                    )
                )

                self.credentials = (
                    flow.run_local_server(port=0)
                )

            self.token.write_text(
                self.credentials.to_json(),
                encoding="utf-8"
            )

        self.youtube = build(
            "youtube",
            "v3",
            credentials=self.credentials
        )

        return self.youtube

    def enviar_video(
        self,
        caminho_video,
        titulo,
        descricao="",
        tags=None,
        categoria="22",
        privacidade="private"
    ):
        """
        Faz upload de um vídeo.

        Retorna o ID do vídeo publicado.
        """

        if tags is None:
            tags = []

        if self.youtube is None:
            self.autenticar()

        body = {

            "snippet": {

                "title": titulo,

                "description": descricao,

                "tags": tags,

                "categoryId": categoria

            },

            "status": {

                "privacyStatus": privacidade,

                "selfDeclaredMadeForKids": False

            }

        }

        media = MediaFileUpload(
            caminho_video,
            resumable=True
        )

        request = self.youtube.videos().insert(

            part="snippet,status",

            body=body,

            media_body=media

        )

        response = None

        while response is None:

            status, response = request.next_chunk()

            if status:

                print(
                    f"Upload: "
                    f"{int(status.progress() * 100)}%"
                )

        print()

        print("Upload concluído!")

        print(
            "ID:",
            response["id"]
        )

        return response["id"]