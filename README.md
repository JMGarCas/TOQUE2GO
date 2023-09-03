<div align="center">
  <img src="./static/banner.png" style="align:center">
</div>

# TOQUE2GO

## Catering Service Web Application made with Python and Flask

Welcome to TOQUE2GO! This web application allows users to arrange appointments with a selection of talented chefs for their events. Whether it's a family dinner, a corporate event, or a special celebration, this app makes it easy to connect with experienced chefs to create memorable culinary experiences.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Docker](#docker)
  - [With Docker Compose](#docker)
  - [Without Docker Compose](#docker)
- [Contributing](#contributing)
- [Technologies Used](#technologies-used)

## Features

- Fully responsive, works on all screens.
- Client and server validation for all the inputs on the website.
- User authentication and profile management for both customers and chefs.
- Admin dashboard to manage user accounts.
- Premium user feature with access to exclusive benefits.
- Filter chefs based on cuisine type, ubication and cost.
- Arrange an appointment with a chef for your events based on the number of people and date.
- Check and manage all your arranged appointments. If you are a chef, accept or decline them.
- Become a chef and show the world your mastery.
- Write and read reviews from other chefs.

## Installation

Follow these steps to get TOQUE2GO up and running on your local machine:

1. Clone the repository:
```
git clone https://github.com/JMGarCas/TOQUE2GO.git
cd TOQUE2GO
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Run the application:
```
flask run
```

4. Access the application:
   
Open a web browser and navigate to http://localhost:5000 to access TOQUE2GO.

## Docker

### - With Docker Compose

1. Open a terminal and navigate to the root directory of the project where the `docker-compose.yml` file is located.

2. Run the following command to build and start the services defined in the `docker-compose.yml` file:
````
docker compose up
````

3. Open a web browser and navigate to http://localhost:5000 to access TOQUE2GO running in a Docker container managed by `docker-compose`.

### - Without Docker Compose

1. Open a terminal and navigate to the root directory of the project where the Dockerfile is located.
   
2. Run the following command to build the Docker image:
```
docker build -t toque2go .
```

3. Once the image is built, you can run a container based on this image using the following command:
```
docker run -p 5000:5000 toque2go
```

4. Open a web browser and navigate to http://localhost:5000 to access TOQUE2GO running in the Docker container.
   
## Contributing

We welcome contributions to TOQUE2GO! If you'd like to contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them.
4. Push your changes to your forked repository.
5. Create a pull request describing your changes.

## Technologies Used

- [Python](https://www.python.org/): A versatile and widely used programming language known for its readability and extensive libraries.
- [Bootstrap](https://getbootstrap.com/): A popular front-end framework for creating responsive and visually appealing web interfaces.
- [Flask](https://flask.palletsprojects.com/en/2.3.x/): A lightweight and flexible Python web framework used for building web applications.
- [Jinja](https://jinja.palletsprojects.com/en/3.1.x/): A templating engine integrated with Flask to dynamically generate HTML content in web applications.
- [CSS](https://developer.mozilla.org/es/docs/Web/CSS): Cascading Style Sheets, used to design the layout and appearance of web pages.
- [HTML](https://developer.mozilla.org/es/docs/Web/HTML): Hypertext Markup Language, the standard markup language for creating web pages and structures.
- [SQLite](https://www.sqlite.org/index.html): A self-contained, serverless, and lightweight relational database management system often used for embedded systems and smaller applications.
- [Docker](https://www.docker.com/): A platform for developing, shipping, and running applications in isolated containers.
- [Docker Compose](https://docs.docker.com/compose/): A tool for defining and running multi-container Docker applications.
- [Git](https://git-scm.com/): A distributed version control system used for tracking changes in code and collaborating on software development projects.
