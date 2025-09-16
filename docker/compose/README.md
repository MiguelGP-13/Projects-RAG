# Compose
## Prerequisites
Have Docker desktop downloaded.

If you don't have it, you can download it [here](https://docs.docker.com/get-started/introduction/get-docker-desktop/).

## Quick start
Download the docker-compose and create a `.env` (called .env) file in the same directory with the following variables:
```env
DB_PASSWORD=<REDIS_PASSWORD>
API_MISTRAL=<Mistral API>
API_HUGGINGFACE=<HuggingFace API>
```
> [!NOTE] 
> The only api key needed is the one you are going to use shown in the settings.env file

To get a Mistral API:
1. Create an account or login if you alredy have one at [Mistral](https://auth.mistral.ai/ui/login).
2. Go to the [api key](https://console.mistral.ai/api-keys) section and click on `Create a new Key`.
3. Copy the key and put it in the .env file.

To get a HuggingFace API:
1. Create an account or login if you alredy have one at [HuggingFace](https://huggingface.co/login).
2. Go to the [Acess Tokens](https://huggingface.co/settings/tokens) section and click on `Create new token`.
3. Copy the key and put it in the .env file.

For the `DB_PASSWORD`, you can use any password you want.

## To run the app:
### Manually 
1. Open Docker Desktop go to this folder and open a terminal. Write
```bash
docker compose up
```
Then you have to open `http://localhost:1380/main.html` in your favourite browser and enjoy.

### Automatic
Run the `quick_start.sh` (linux) or the `quick_start.bat` (windows) script that will deploy the app.
