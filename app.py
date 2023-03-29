from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from flask_marshmallow import Marshmallow
import json

app = Flask(__name__)
api = Api(app)

app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://root:root1234@localhost:3306/flasktaskdb'

db = SQLAlchemy(app)
ma = Marshmallow(app)

class Department(db.Model):
    __tablename__ = 'department2'
    dept_id = db.Column(db.Integer, primary_key=True)
    dept_name = db.Column(db.String(15), nullable=False)

    def serialize(self):
        return {
            'dept_id'   : self.dept_id,
            'dept_name' : self.dept_name

        }

with app.app_context():
    db.create_all()


class deptSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Department
    
    dept_id = ma.auto_field()
    dept_name = ma.auto_field()
    

dept_schema = deptSchema()
dept_schemas = deptSchema(many=True)







class HelloWorld(Resource):
    def get(self):
        print("App is working")
        return {
            'data' : 'The app is working Fine.'
        }
    

class GetDataFromDepartment(Resource):
    def get(self):
        try:
            data = Department.query.all()
            udata = dept_schemas.dumps(data)
            data = json.loads(udata)
            return data
        except Exception as e:
            df = {
                "Error_Status" : "404 Bad Request",
                "Error_Message" : e.args[0]
                }
            print("Error Message :", e.args[0])
            return df
    
    def post(self):
        try:
            data = Department(dept_name = request.json['name'])
            db.session.add(data)
            db.session.commit()
            dept_schema.dumps(data)
            return ("Data added to Department")
        except Exception as e:
            df = {
                "Error_Status" : "404 Bad Request",
                "Error_Message" : e.args[0]
            }
            print("Error Message :", e.args[0])
            return df

           
class GetDataFromDepartmentbyID(Resource):
    def get(self, dept_id):
        try:
            data = Department.query.filter_by(dept_id=dept_id)
            udata = dept_schemas.dumps(data)
            data = json.loads(udata)
            return data
        except Exception as e:
            df = {
                "Error_Status" : "404 Bad Request",
                "Error_Message" : e.args[0]
            }
            print("Error Message :", e.args[0])
            return df
        
    


api.add_resource(HelloWorld, '/')
api.add_resource(GetDataFromDepartment, '/GetDataFromDepartment')
api.add_resource(GetDataFromDepartmentbyID, '/GetDataFromDepartmentbyID/<int:dept_id>')

if __name__ == '__main__':
    app.run(debug=True)