# CulinaryConnect

CulinaryConnect is a recipe sharing platform where users can share their favorite recipes, discover new ones, and connect with other cooking enthusiasts.

## Features

- **User Authentication**: Sign up, login, and secure user profiles
- **Recipe Management**: Create, read, update, and delete recipes
- **Recipe Categorization**: Organize recipes by categories
- **Ingredient Management**: Add ingredients with quantities and measurements
- **Comments**: Share thoughts and feedback on recipes
- **Favorites**: Save recipes to your favorites for easy access
- **User Profiles**: View user profiles and their recipe collections

## Database Schema

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    User     │     │   Recipe    │     │  Category   │
├─────────────┤     ├─────────────┤     ├─────────────┤
│ id          │1───N│ id          │N───M│ id          │
│ username    │     │ title       │     │ name        │
│ email       │     │ description │     │ description │
│ password    │     │ prep_time   │     └─────────────┘
│ profile_pic │     │ cook_time   │            
│ created_at  │     │ servings    │            
└─────────────┘     │ image_url   │      ┌─────────────┐
       │1           │ created_at  │      │ Ingredient  │
       │            │ user_id     │      ├─────────────┤
       │            └─────────────┘      │ id          │
       │                   │1            │ name        │
       │                   │             │ unit        │
       │            ┌─────────────┐      └─────────────┘
       │        1  N│RecipeIngred.│             │1
       │            ├─────────────┤             │
       │            │ id          │             │
       │            │ recipe_id   │N───────────1│
       │            │ ingred_id   │             │
       │            │ quantity    │             │
       │            └─────────────┘             │
       │                                         │
       │1           ┌─────────────┐             │
       └───────────N│  Comment    │             │
       │1           ├─────────────┤             │
       │            │ id          │             │
       │            │ content     │             │
       │            │ created_at  │             │
       │            │ recipe_id   │             │
       │            │ user_id     │             │
       │            └─────────────┘             │
       │                                         │
       │            ┌─────────────┐             │
       └───────────N│  Favorite   │             │
                    ├─────────────┤             │
                    │ id          │             │
                    │ user_id     │             │
                    │ recipe_id   │             │
                    └─────────────┘             │
```

## Tech Stack

- **Backend**: Flask, SQLAlchemy, Flask-Login, Flask-WTF
- **Frontend**: Bootstrap 5, Font Awesome, JavaScript
- **Database**: SQLite (development), PostgreSQL (production)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/culinaryconnect.git
   cd culinaryconnect
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```
   flask db init
   flask db migrate
   flask db upgrade
   ```

5. Run the application:
   ```
   python app.py
   ```

## Project Structure

```
culinaryconnect/
├── app/                    # Application package
│   ├── auth/               # Authentication routes, forms, tests
│   ├── main/               # Main routes, forms, tests
│   ├── static/             # Static files (CSS, JS)
│   ├── templates/          # HTML templates
│   ├── models.py           # Database models
│   ├── extensions.py       # Flask extensions
│   └── config.py           # Configuration settings
├── requirements.txt        # Project dependencies
├── app.py                  # Application entry point
└── README.md               # Project documentation
```

## Contribution

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.