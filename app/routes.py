from datetime import datetime
from flask import Flask, render_template, flash, redirect, url_for, request, jsonify
from werkzeug.urls import url_parse
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EmptyForm, PostForm, MetricForm
from app.models import User, Post, Metric
import flask_excel as excel

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))
    
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title='Home', form=form,
                            posts=posts.items, next_url=next_url,
                            prev_url=prev_url)

@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template("index.html", title='Explore', posts=posts.items,
                          next_url=next_url, prev_url=prev_url)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)
	
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

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
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url, form=form)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)


@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash('You are following {}!'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))


@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash('You are not following {}.'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))




@app.route('/metrics', methods=['GET', 'POST'])
@login_required
def list_metrics():
    metrics = Metric.query.all()

    return render_template('metrics.html',
                            metrics=metrics, title="Metrics")



@app.route('/metrics/add', methods=['GET', 'POST'])
@login_required
def add_metric():

    add_metric = True

    form = MetricForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        metric = Metric(
        creator=current_user,
        service_name = form.service_name.data,
        service_element_name = form.service_element_name.data,
        service_level_detail = form.service_level_detail.data ,
        target = form.target.data,
        service_provider_steward_1 = form.service_provider_steward_1.data,
        metric_name = form.metric_name.data,
        metric_description = form.metric_description.data,
        metric_rationale = form.metric_rationale.data,
        metric_value_display_format = form.metric_value_display_format.data,
        threshold_target = form.threshold_target.data,
        threshold_target_rationale = form.threshold_target_rationale.data,
        threshold_target_direction = form.threshold_target_direction.data,
        threshold_trigger = form.threshold_trigger.data,
        threshold_trigger_rationale = form.threshold_trigger_rationale.data,
        threshold_trigger_direction = form.threshold_trigger_direction.data,
        data_source = form.data_source.data,
        data_update_frequency = form.data_update_frequency.data,
        metric_owner_primary = form.metric_owner_primary.data,
        vantage_control_id = form.vantage_control_id.data)     
        db.session.add(metric)
        db.session.commit()
        flash('New metric added')
        return redirect(url_for('list_metrics'))

    return render_template('/metric.html', action="Add", add_metric=add_metric, title='Add Metrics', form=form)


@app.route('/metrics/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_metric(id):

    add_metric = False

    metric = Metric.query.get_or_404(id)
    form = MetricForm(obj=metric)
    if form.validate_on_submit():

        metric.service_name = form.service_name.data
        metric.service_element_name = form.service_element_name.data
        metric.service_level_detail = form.service_level_detail.data
        metric.target = form.target.data
        metric.service_provider_steward_1 = form.service_provider_steward_1.data
        metric.metric_name = form.metric_name.data
        metric.metric_description = form.metric_description.data
        metric.metric_rationale = form.metric_rationale.data
        metric.metric_value_display_format = form.metric_value_display_format.data
        metric.threshold_target = form.threshold_target.data
        metric.threshold_target_rationale = form.threshold_target_rationale.data
        metric.threshold_target_direction = form.threshold_target_direction.data
        metric.threshold_trigger = form.threshold_trigger.data
        metric.threshold_trigger_rationale = form.threshold_trigger_rationale.data
        metric.threshold_trigger_direction = form.threshold_trigger_direction.data
        metric.data_source = form.data_source.data
        metric.data_update_frequency = form.data_update_frequency.data
        metric.metric_owner_primary = form.metric_owner_primary.data
        metric.vantage_control_id = form.vantage_control_id.data     
        db.session.commit()
        flash('Your metric changes have been saved')
        return redirect(url_for('list_metrics'))
    elif request.method == 'GET':
        form.service_name.data = metric.service_name
        form.service_element_name.data = metric.service_element_name
        form.service_level_detail.data = metric.service_level_detail
        form.target.data = metric.target
        form.service_provider_steward_1.data = metric.service_provider_steward_1
        form.metric_name.data = metric.metric_name
        form.metric_description.data = metric.metric_description
        form.metric_rationale.data = metric.metric_rationale
        form.metric_value_display_format.data = metric.metric_value_display_format
        form.threshold_target.data = metric.threshold_target
        form.threshold_target_rationale.data = metric.threshold_target_rationale
        form.threshold_target_direction.data = metric.threshold_target_direction
        form.threshold_trigger.data = metric.threshold_trigger
        form.threshold_trigger_rationale.data = metric.threshold_trigger_rationale
        form.threshold_trigger_direction.data = metric.threshold_trigger_direction
        form.data_source.data = metric.data_source
        form.data_update_frequency.data = metric.data_update_frequency
        form.metric_owner_primary.data = metric.metric_owner_primary
        form.vantage_control_id.data = metric.vantage_control_id

    return render_template('metric.html', title='Edit Metric', action="Edit",
                           add_metric=add_metric, form=form,
                           metric=metric)


@app.route('/metrics/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_metric(id):
   
    metric = Metric.query.get_or_404(id)
    db.session.delete(metric)
    db.session.commit()
    flash('You have successfully deleted the metric.')

    # redirect to the departments page
    return redirect(url_for('list_metrics'))

    return render_template(title="Delete Metric")


@app.route("/import", methods=['GET', 'POST'])
def doimport():
    if request.method == 'POST':

        def metric_init_func(row):
            m = Metric(
                row['service_name'],
                row['service_element_name'],
                row['service_level_detail'],
                row['target'],
                row['service_provider_steward_1'],
                row['metric_name'],
                row['metric_description'],
                row['metric_rationale'],
                row['metric_value_display_format'],
                row['threshold_target'],
                row['threshold_target_rationale'],
                row['threshold_target_direction'],
                row['threshold_trigger'],
                row['threshold_trigger_rationale'],
                row['threshold_trigger_direction'],
                row['data_source'],
                row['data_update_frequency'],
                row['metric_owner_primary'],
                row['vantage_control_id'])
            return m
        request.save_book_to_database(
            field_name='file', session=db.session,
            tables=[Metric],
            initializers=[metric_init_func])
        return redirect(url_for('.handson_table'), code=302)
    return '''
    <!doctype html>
    <title>Upload an excel file</title>
    <h1>Excel file upload (xls, xlsx, ods please)</h1>
    <form action="" method=post enctype=multipart/form-data><p>
    <input type=file name=file><input type=submit value=Upload>
    </form>
    '''
@app.route("/handson_view", methods=['GET'])
def handson_table():
    return excel.make_response_from_tables(
        db.session, [Metric], 'handsontable.html')