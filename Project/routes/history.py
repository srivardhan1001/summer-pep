from flask import Blueprint, render_template, jsonify, request
from models.history import SearchHistory
from models import db
from forms import ClearHistoryForm

history_bp = Blueprint('history', __name__)


@history_bp.route('/history')
def view_history():
    history_items = SearchHistory.query.order_by(SearchHistory.created_at.desc()).limit(50).all()
    # ClearHistoryForm is passed to the template so it can render its CSRF
    # token alongside the "Clear All History" button.
    form = ClearHistoryForm()
    return render_template('history.html', history_items=history_items, form=form)


# ------------------------------------------------------------------ #
#  JSON API endpoints — all CSRF-exempted in app.py                  #
# ------------------------------------------------------------------ #

@history_bp.route('/api/history', methods=['GET'])
def get_history_api():
    history_items = SearchHistory.query.order_by(SearchHistory.created_at.desc()).limit(10).all()
    return jsonify({'success': True, 'history': [item.to_dict() for item in history_items]})


@history_bp.route('/api/history/<int:item_id>', methods=['DELETE'])
def delete_history_item(item_id):
    item = SearchHistory.query.get(item_id)
    if not item:
        return jsonify({'success': False, 'error': 'History item not found'}), 404

    db.session.delete(item)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Item deleted'})


@history_bp.route('/api/history/clear', methods=['DELETE', 'POST'])
def clear_all_history():
    SearchHistory.query.delete()
    db.session.commit()
    return jsonify({'success': True, 'message': 'History cleared'})
