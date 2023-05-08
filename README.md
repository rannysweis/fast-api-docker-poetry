# Fast Api / Docker / Poetry 

## Contents
1. [Requirments](https://github.com/rannysweis/fast-api-docker-poetry#Requirments)
2. [Best Practices](https://github.com/rannysweis/fast-api-docker-poetry#Best-Practices)
3. [File structure](https://github.com/rannysweis/fast-api-docker-poetry#File-structure)
4. [Quick Start](https://github.com/rannysweis/fast-api-docker-poetry#Quick-Start)

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
3. Use `@cbv` decorator to initialize shared dependencies.
   ```
      @cbv(order_router)
      class OrderController:
          def __init__(self):
              self.order_service = OrderService()
   ```
4. Log and raise original DB exceptions
   ```
      try:
          ...
      except IntegrityError as e:
          logger.exception(f'{self.__model__.__name__} error: {e.orig}')
          raise e
      except ProgrammingError as e:
          logger.exception(f'{self.__model__.__name__} error: {e}')
          raise e
   ```
5. Model files has ORM and pydantic classes for easier updates (Might not be the best solution for all)
   - Schema - request/response object. It uses `BaseSchema.to_orm` to convert to ORM
   - ORM - DB object



## File structure
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



## Quick Start

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

