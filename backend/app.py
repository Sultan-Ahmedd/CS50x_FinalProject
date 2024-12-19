
from flask import Flask, render_template, redirect, url_for, flash, request
from config import Config
from models import db, User, Recipe, Comment, Rating
from forms import RegistrationForm, LoginForm, RecipeForm, CommentForm, RatingForm
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask_migrate import Migrate
from markupsafe import Markup, escape  

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)

login = LoginManager(app)
login.login_view = 'login'

@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.template_filter('nl2br')
def nl2br_filter(s):
    if s is None:
        return ''
    escaped = escape(s)
    return Markup(escaped.replace('\n', '<br>\n'))

@app.route('/')
def index():
    recipes = Recipe.query.order_by(Recipe.timestamp.desc()).all()
    return render_template('index.html', recipes=recipes)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now registered!')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('index'))
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/create_recipe', methods=['GET', 'POST'])
@login_required
def create_recipe():
    form = RecipeForm()
    if form.validate_on_submit():
        recipe = Recipe(
            title=form.title.data,
            ingredients=form.ingredients.data,
            instructions=form.instructions.data,
            image_url=form.image_url.data,
            category=form.category.data,
            author=current_user
        )
        db.session.add(recipe)
        db.session.commit()
        flash('Your recipe has been created!')
        return redirect(url_for('index'))
    return render_template('create_recipe.html', form=form)

@app.route('/recipe/<int:recipe_id>', methods=['GET', 'POST'])
def view_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    form_comment = CommentForm()
    form_rating = RatingForm()
    if form_comment.validate_on_submit() and 'comment_submit' in request.form:
        if not current_user.is_authenticated:
            flash('You need to be logged in to comment.')
            return redirect(url_for('login'))
        comment = Comment(
            comment_text=form_comment.comment_text.data,
            recipe=recipe,
            author=current_user
        )
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been added.')
        return redirect(url_for('view_recipe', recipe_id=recipe.id))
    if form_rating.validate_on_submit() and 'rating_submit' in request.form:
        if not current_user.is_authenticated:
            flash('You need to be logged in to rate.')
            return redirect(url_for('login'))
        rating = Rating(
            rating_value=form_rating.rating_value.data,
            recipe=recipe,
            author=current_user
        )
        db.session.add(rating)
        db.session.commit()
        flash('Your rating has been submitted.')
        return redirect(url_for('view_recipe', recipe_id=recipe.id))
    comments = recipe.comments.order_by(Comment.timestamp.asc()).all()
    ratings = recipe.ratings.all()
    average_rating = sum([r.rating_value for r in ratings]) / len(ratings) if ratings else None
    return render_template('view_recipe.html', recipe=recipe, comments=comments, average_rating=average_rating, form_comment=form_comment, form_rating=form_rating)

@app.route('/edit_recipe/<int:recipe_id>', methods=['GET', 'POST'])
@login_required
def edit_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.author != current_user:
        flash('You cannot edit this recipe.')
        return redirect(url_for('view_recipe', recipe_id=recipe.id))
    form = RecipeForm(obj=recipe)
    if form.validate_on_submit():
        recipe.title = form.title.data
        recipe.ingredients = form.ingredients.data
        recipe.instructions = form.instructions.data
        recipe.image_url = form.image_url.data
        recipe.category = form.category.data
        db.session.commit()
        flash('Your recipe has been updated.')
        return redirect(url_for('view_recipe', recipe_id=recipe.id))
    return render_template('create_recipe.html', form=form, edit=True)

@app.route('/delete_recipe/<int:recipe_id>', methods=['POST'])
@login_required
def delete_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.author != current_user:
        flash('You cannot delete this recipe.')
        return redirect(url_for('view_recipe', recipe_id=recipe.id))
    db.session.delete(recipe)
    db.session.commit()
    flash('Your recipe has been deleted.')
    return redirect(url_for('index'))

@app.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    recipes = user.recipes.order_by(Recipe.timestamp.desc()).all()
    return render_template('profile.html', user=user, recipes=recipes)

if __name__ == '__main__':
    app.run(debug=True)
