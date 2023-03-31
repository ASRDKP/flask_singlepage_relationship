from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from flask_marshmallow import Marshmallow
import json
from marshmallow import Schema, fields

app = Flask(__name__)
api = Api(app)

app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://root:root1234@localhost:3306/flasktaskdb'

db = SQLAlchemy(app)
ma = Marshmallow(app)

class Department(db.Model):
    __tablename__ = 'department2'
    dept_id = db.Column(db.Integer, primary_key=True)
    dept_name = db.Column(db.String(15), nullable=False)

    def __repr__(self):
        return f"Department(dept_id={self.dept_id}, dept_name='{self.dept_name}')"
            
    # def serialize(self):
    #     return {
    #         'dept_id'   : self.dept_id,
    #         'dept_name' : self.dept_name

    #     }
    
        
class Employee(db.Model):
    __tablename__ = 'empdetails'
    emp_id = db.Column(db.Integer, primary_key=True)
    emp_name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    postion = db.Column(db.String(35), nullable=False)
    email = db.Column(db.String(75), unique=True, nullable=False)
    salary = db.Column(db.Integer, nullable=False)
    contact = db.Column(db.Integer, nullable=False)
    dept_id = db.Column(db.Integer, db.ForeignKey('department2.dept_id'), nullable=False)
    dept_info = db.relationship('Department')
    
    def __repr__(self):
        return f"Employee(emp_id={self.emp_id}, emp_name='{self.emp_name}', surname='{self.surname}', postion='{self.postion}', email='{self.email}', salary='{self.salary}', contact='{self.contact}', dept_id='{self.dept_id}')"
    # def serialize(self):
    #     return{
    #         'emp_id'  : self.emp_id,
    #         'emp_name': self.emp_name,
    #         'surname' : self.surname,
    #         'postion' : self.postion,
    #         'email'   : self.email,
    #         'salary'  : self.salary,
    #         'contact' : self.contact,
    #         'dept_id' : self.dept_id,
    #     }
    



with app.app_context():
    db.create_all()


class deptSchema(Schema):

    dept_id = fields.Int(dump_only=True)
    dept_name = fields.Str()
    emp_info = fields.List(fields.Nested(lambda: empSchema(exclude=("dept_info","dept_id",)), many=True))

dept_schema  = deptSchema()
dept_schemas = deptSchema(many=True)

                   

# class empSchema(ma.SQLAlchemySchema):
#     class Meta:
#         model = Employee
        
#     emp_id   = ma.auto_field()
#     emp_name = ma.auto_field()
#     surname  = ma.auto_field()
#     dept_id  = ma.auto_field()
#     postion  = ma.auto_field()
#     email    = ma.auto_field()
#     salary   = ma.auto_field()
#     contact  = ma.auto_field()
#     # dept_info = ma.Nested(deptSchema)
#     dept_info = ma.HyperlinkRelated(
#         {
#             "self" : ma.URLFor("GetDataFromDepartment", values = dict(dept_id="<dept_id>"))
#         }
        
#     )

class empSchema(Schema):
    
    emp_name = fields.Str()
    surname  = fields.Str()
    emp_id   = fields.Int(dump_only=True)
    postion  = fields.Str()
    email    = fields.Email()
    salary   = fields.Int()
    contact  = fields.Int()
    dept_info = fields.Nested(deptSchema)
    
emp_schema = empSchema()
emp_schemas = empSchema(many=True)



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
            data = Department(dept_name = request.json['dept_name'])
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
        
    def put(self, dept_id):
        try:
            data = Department.query.get_or_404(dept_id)
            if data is None:
                message = "Data with the given Id does not exist."
                print(message)
                return message
            data.dept_id = request.json['dept_id']
            data.dept_name = request.json['dept_name']
            db.session.commit()
            dept_schema.dumps(data)
            return "Data Updated successfully"
        except Exception as e:
            df = {
                "Error_Status" : "404 Bad Request",
                "Error_Message" : e.args[0]
            }
            print("Error_Message :", e.args[0])
            return df          
    
    def delete(self, dept_id):
        try:
            data = Department.query.get_or_404(dept_id)
            if data is None:
                message = "Data with the given Id does not exist."
                print(message)
                return message
            db.session.delete(data)
            db.session.commit()
            dept_schema.dumps(data)
            return "Data Deleted Successfully"
        except Exception as e: 
            df = {
                "Error_Status" : "404 Bad Request",
                "Error_Message" : e.args[0]
            }
            print("Error_Message :", e.args[0])
            return df
        
                       
  
        
class GetDataFromEmployee(Resource):
    def get(self):
        try:
            data = Employee.query.all()
            udata = emp_schemas.dumps(data)
            data = json.loads(udata)
            return data
            # return [Employee.serialize(record) for record in data]
        except Exception as e:
            df = {
                "Error_Status" : "404 Bad Request",
                "Error_Message" : e.args[0]
            }
            print("Error_Message :", e.args[0])
            return df
                

    def post(self):
        try:
            data = Employee(emp_name = request.json['emp_name'],surname  = request.json['surname'],dept_id  = request.json['dept_id'],postion  = request.json['postion'],email    = request.json['email'],salary  = request.json['salary'],contact = request.json['contact'])
            db.session.add(data)
            db.session.commit()
            emp_schema.dumps(data)
            return ("Data added to Department")
        except Exception as e:
            df = {
                "Error_Status" : "404 Bad Request",
                "Error_Message" : e.args[0]
            }
            print("Error : ", e.args[0])
            return df


class GetDataFromEmployeebyID(Resource):
 
    def get(self, emp_id):
        try:
            data = Employee.query.filter_by(emp_id = emp_id)
            udata = emp_schemas.dumps(data)
            data = json.loads(udata)
            return data
        except Exception as e:
            df = {
                "Error_Status" : "404 Bad Request",
                "Error_Message" : e.args[0]
            }
            print("Error :", e.args[0])
            return df
        
    def put(self, emp_id):
        try:
            data = Employee.query.get_or_404(emp_id)
            if data is None:
                message = "Data with the given Id does not exist."
                print(message)
                return message
            data.emp_name = request.json['emp_name']
            data.surname = request.json['surname']
            data.dept_id = request.json['dept_id']
            data.postion = request.json['postion']
            data.email = request.json['email']
            data.salary = request.json['salary']
            data.contact = request.json['contact']
            db.session.commit()
            emp_schema.dumps(data)
            return "Data Updated successfully"
        except Exception as e:
            df = {
                "Error_Status" : "404 Bad Request",
                "Error_Message" : e.args[0]
            }
            print("Error :", e.args[0])
            return df       
    
 
    def delete(self, emp_id):
        try:
            data = Employee.query.get_or_404(emp_id)
            if data is None:
                message = "Data with the given Id does not exist."
                print(message)
                return message
            db.session.delete(data)
            db.session.commit()
            emp_schema.dumps(data)
            return "Data Deleted Successfully"
        except Exception as e:
            df = {
                "Error_Status" : "404 Bad Request",
                "Error_Message" : e.args[0]
            }
            print("Error : ", e.args[0])
            return df

api.add_resource(HelloWorld, '/')
api.add_resource(GetDataFromDepartment, '/GetDataFromDepartment')
api.add_resource(GetDataFromDepartmentbyID, '/GetDataFromDepartmentbyID/<int:dept_id>')

api.add_resource(GetDataFromEmployee, '/GetDataFromEmployee')
api.add_resource(GetDataFromEmployeebyID, '/GetDataFromEmployeebyID/<int:emp_id>')

if __name__ == '__main__':
    app.run(debug=True)
    
    
    
