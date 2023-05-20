import asyncio
import azure.identity
import httpx
import kiota_abstractions.api_error
import kiota_authentication_azure.azure_identity_authentication_provider
import msgraph
import msgraph.generated.models.user_collection_response
import msgraph_core
import pydantic
import traceback
import typing


class Settings(pydantic.BaseSettings):
    client_id: str
    tenant_id: str

settings = Settings()

credential = azure.identity.DeviceCodeCredential(
    client_id=settings.client_id,
    tenant_id=settings.tenant_id
)
scopes = ['User.ReadBasic.All']
auth_provider = kiota_authentication_azure.azure_identity_authentication_provider.AzureIdentityAuthenticationProvider(credential, scopes=scopes)
http_client = msgraph_core.GraphClientFactory.create_with_default_middleware(client=httpx.AsyncClient())
request_adapter = msgraph.GraphRequestAdapter(auth_provider, http_client)
client = msgraph.GraphServiceClient(request_adapter)

async def get_user_display_name_and_photo(user_id: str) -> typing.Tuple[typing.Optional[msgraph.generated.models.user_collection_response.UserCollectionResponse], bytes]:
    try:
        user_item_request_builder = client.users.by_user_id(user_id)
        user = await user_item_request_builder.get()
        profile_picture = await user_item_request_builder.photo.content.get()
    except kiota_abstractions.api_error.APIError as e:
        error_message = e.error.message if e.error else str(e)
        print(f'Error fetching profile picture for user {user_id}: {error_message}')
        print(traceback.format_exc())
    else:
        return (user, profile_picture)

async def main():
    user_id = 'MeganB@M365x214355.onmicrosoft.com'
    (user, photo) = await get_user_display_name_and_photo(user_id)
    if user:
        print(user.display_name)
        if photo:
            with open(f"{user_id[:user_id.index('@')]}.jpg", "wb") as file:
                file.write(photo)
        else:
            print("No picture.")

asyncio.run(main())
