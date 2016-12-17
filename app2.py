from flask import Flask, request, json
from app2.model import createDB
from app2.model import db
from app2.model import Expenses
app = Flask(__name__)
import redis

#createDB()
db.create_all()
@app.route('/v1/expenses/<int:expense_id>', methods = ['GET'])
def getExpense(expense_id):
    expense = Expenses.query.filter_by(id=expense_id).first_or_404()
    return json.dumps({'id': expense.id, 'name': expense.name, 'email': expense.email, 'category': expense.category, 'description': expense.description, 'link': expense.link, 'estimated_costs': expense.estimated_costs, 'submit_date': expense.submit_date, 'status': "Pending", 'decision_date': expense.decision_date})

@app.route('/v1/expenses', methods= ['POST'])
def addExpense():
        getAttribute = request.get_json(force=True)
        expense = Expenses(getAttribute ['name'], getAttribute['email'], getAttribute['category'],
                           getAttribute['description'], getAttribute['link'], getAttribute['estimated_costs'],
                           getAttribute['submit_date'], status='pending', decision_date='')
        db.session.add(expense)
        db.session.commit()
        return json.dumps({'id': expense.id, 'name': expense.name, 'email': expense.email,'category':expense.category,
                           'description' : expense.description, 'link': expense.link, 'estimated_costs' : expense.estimated_costs,
                           'submit_date': expense.submit_date, 'status': "Pending", 'decision_date': expense.decision_date}), 201

@app.route('/v1/expenses/<int:expense_id>', methods = ['DELETE'])
def removeExpense(expense_id):
    expense = Expenses.query.filter_by(id=expense_id).first_or_404()
    db.session.delete(expense)
    db.session.commit()
    return json.dumps({}), 204

@app.route('/v1/expenses/<int:expense_id>', methods = ['PUT'])
def updateExpense(expense_id):
    expense = Expenses.query.filter_by(id=expense_id).first_or_404()
    getAttribute = request.get_json(force=True)
    expense.estimated_costs = getAttribute['estimated_costs']
    db.session.commit()
    return json.dumps({}), 202

if __name__== "__main__":
    host = '0.0.0.0'
    port = 5002
    r = redis.Redis('127.0.0.1', 6379)
    r.rpush('activeServersList', host + ":" + str(port))
    app.run(host=host, port=port)


