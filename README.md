# Compose
## Prerequisites
Have Docker desktop downloaded.

If you don't hav it, you can download it [here](https://docs.docker.com/get-started/introduction/get-docker-desktop/).

## Quick start
Download the docker-compose and create a `.env` (called .env) file in the same directory with the following variables:
```env
DB_PASSWORD=<REDIS_PASSWORD>
API_MISTRAL=<Mistral API>
```
To get a Mistral API:
1. Create an account or login if you alredy have one at [Mistral](https://auth.mistral.ai/ui/login?flow=da5da21c-a399-493c-9a19-61ee7dd3319c).
2. Go to the [api key](https://console.mistral.ai/api-keys) section and click on `Create a new Key`.
3. Copy the key and put it in the .env file.

For the `DB_PASSWORD`, you can use any password you want.

To run the app, 
1. Open Docker Desktop go to this folder and open a terminal. Write
```bash
docker compose up
```
Then you have to open `http://localhost:1380/main.html` in your favourite browser and enjoy.

## Code 
This branch has the necessary code to build both images and do the docker compose.

We also provide a `quick_start.sh` script that will deploy the app.
