# Fast Api / Docker / Poetry 

## Requirments
 - docker
 - docker compose
 - poetry

## Best Practices

1. Naming conventions
   1. Every file should have a unique name
   2. Add type to file name outside of models. I believe it helps with search-ability/readability 
      ```
      order_controller, order_service, order_repository
      ```
2. Set custom exception_handler in `main.py` to better format error responses
   ```
      application.add_exception_handler(HTTPException, exh.http_exception_handler)
   ```


### File structure
```
fast-api-docker-poetry 
├── app
│   ├── config                                --  app configs
│   │   ├── exception_handlers.py        
│   │   ├── settings.py                  
│   ├── controllers                           --  api routes by objects
│   │   ├── order_controller.py 
│   └── models                                --  orm and pydantic models
│   │   ├── order.py
│   │   ├── address.py
│   │   ├── base.py
│   │   ├── pageable.py
│   └── repository                            --  database queries
│   │   ├── order_repository.py
│   └── services                              --  business logic / data transformation
│   │   ├── order_service.py
│   └── utils
│   │   ├── db.py
│   └── main.py
├── migrations/                               --  alembic migrations
├── tests/
│   ├── integrations                          --  test api routes by using TestClient
├── .env
├── .gitignore
├── docker-compose.yml
├── Makefile
├── pyproject.toml
└── alembic.ini
```



# Quick Start

1. Start with docker
    ```
    make startd
    ```
2. Test with docker
    ```
    make testd
    ```
3. Start with poetry
    ```
    make startp
    ```
4. Test with poetry
    ```
    make testp
    ```

