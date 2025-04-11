# Real-Time Chat Application

This is a real-time chat application built with FastAPI, SQLAlchemy, WebSockets, and PostgreSQL. It supports multiple chat rooms, message history, and user authentication.

## Features

- **Real-time Messaging**: Users can send and receive messages in real time using WebSockets.
- **Chat Rooms**: Create and join different chat rooms.
- **User Authentication**: Secure user authentication using JWT tokens.
- **Message History**: All messages are stored in PostgreSQL for easy access and retrieval.
- **Email Verification**: Users receive an email with a verification link upon registration.

## Technologies Used

- **FastAPI**: Web framework for building APIs.
- **SQLAlchemy**: ORM for database interaction.
- **PostgreSQL**: Relational database for storing user data and messages.
- **JWT**: For authentication and secure token handling.
- **Alembic**: For database migrations.
- **Poetry**: Dependency management and packaging tool for Python.


### Prerequisites

- Python 3.9 or higher
- Docker (optional, for containerization)
- PostgreSQL instance (can be set up via Docker)
