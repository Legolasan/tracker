from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.database import db
from app.models.application import Application
from app.models.document import Document, DocumentType

documents_bp = Blueprint('documents', __name__, url_prefix='/documents')


@documents_bp.route('/new')
@login_required
def new():
    application_id = request.args.get('application_id', type=int)
    application = None
    
    if application_id:
        application = Application.query.filter_by(id=application_id, user_id=current_user.id).first_or_404()
    
    applications = Application.query.filter_by(user_id=current_user.id).order_by(Application.company).all()
    
    return render_template('documents/form.html',
                         document=None,
                         application=application,
                         applications=applications,
                         type_choices=DocumentType.choices())


@documents_bp.route('/create', methods=['POST'])
@login_required
def create():
    application_id = request.form.get('application_id', type=int)
    application = Application.query.filter_by(id=application_id, user_id=current_user.id).first_or_404()
    
    filename = request.form.get('filename', '').strip()
    document_type = request.form.get('document_type', DocumentType.OTHER)
    url = request.form.get('url', '').strip()
    notes = request.form.get('notes', '').strip()
    
    if not filename:
        flash('Document name is required.', 'error')
        return redirect(url_for('documents.new', application_id=application_id))
    
    document = Document(
        application_id=application_id,
        filename=filename,
        document_type=document_type,
        url=url or None,
        notes=notes or None
    )
    
    db.session.add(document)
    db.session.commit()
    
    flash(f'Document "{filename}" added!', 'success')
    return redirect(url_for('applications.show', id=application_id))


@documents_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    document = Document.query.join(Application).filter(
        Document.id == id,
        Application.user_id == current_user.id
    ).first_or_404()
    
    if request.method == 'POST':
        document.filename = request.form.get('filename', '').strip()
        document.document_type = request.form.get('document_type', DocumentType.OTHER)
        document.url = request.form.get('url', '').strip() or None
        document.notes = request.form.get('notes', '').strip() or None
        
        if not document.filename:
            flash('Document name is required.', 'error')
            return render_template('documents/form.html',
                                 document=document,
                                 application=document.application,
                                 applications=[],
                                 type_choices=DocumentType.choices())
        
        db.session.commit()
        flash('Document updated!', 'success')
        return redirect(url_for('applications.show', id=document.application_id))
    
    return render_template('documents/form.html',
                         document=document,
                         application=document.application,
                         applications=[],
                         type_choices=DocumentType.choices())


@documents_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    document = Document.query.join(Application).filter(
        Document.id == id,
        Application.user_id == current_user.id
    ).first_or_404()
    
    application_id = document.application_id
    db.session.delete(document)
    db.session.commit()
    
    flash('Document removed.', 'info')
    return redirect(url_for('applications.show', id=application_id))

