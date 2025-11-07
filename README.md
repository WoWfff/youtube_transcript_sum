**For correct operation, add the .env file to the root of the project.**

**Name of DB:**
```youtube_transcript```

The file must contain the following lines for your database and GEMINI api key:

```
DB_HOST=database_host
DB_PORT=5432
DB_USER=database_user
DB_PASS=database_password
GEMINI_API_KEY=your_key
```

You can get API key here: [api-keys](https://aistudio.google.com/api-keys)

You also need a postgresql installed on your system.

Only after that, install requirements.txt, otherwise you will have errors.