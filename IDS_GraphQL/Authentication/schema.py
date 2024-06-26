import graphene
from graphene_django import DjangoObjectType
from .models import Login
from django.contrib.auth.hashers import make_password, check_password
from graphql import GraphQLError 


class LoginType(DjangoObjectType):
    class Meta:
        model = Login

class CreateLogin(graphene.Mutation):
    login = graphene.Field(LoginType)

    class Arguments:
        name = graphene.String(required=True)
        phone_num = graphene.String(required=True)
        designation = graphene.String(required=True)
        location = graphene.String(required=True)
        business_unit = graphene.String(required=True)
        role = graphene.String(required=True)
        email = graphene.String(required=True)
        status = graphene.Boolean(required=True)
        password = graphene.String(required=True)

    def mutate(self, info, name, phone_num, designation, location, business_unit, role, email, status, password):
        login = Login(
            name=name,
            phone_num=phone_num,
            designation=designation,
            location=location,
            business_unit=business_unit,
            role=role,
            email=email,
            status=status,
            password=make_password(password)
        )
        login.save()
        return CreateLogin(login=login)


class UpdateLogin(graphene.Mutation):
    login = graphene.Field(LoginType)

    class Arguments:
        id = graphene.String(required=True)
        name = graphene.String()
        phone_num = graphene.String()
        designation = graphene.String()
        location = graphene.String()
        business_unit = graphene.String()
        role = graphene.String()
        email = graphene.String()
        status = graphene.Boolean()
        password = graphene.String()

    def mutate(self, info, id, name=None, phone_num=None, designation=None, location=None, business_unit=None, role=None, email=None, status=None, password=None):
        try:
            login = Login.objects.get(pk=id)
            if name:
                login.name = name
            if phone_num:
                login.phone_num = phone_num
            if designation:
                login.designation = designation
            if location:
                login.location = location
            if business_unit:
                login.business_unit = business_unit
            if role:
                login.role = role
            if email:
                login.email = email
            if status is not None:
                login.status = status
            if password:
                login.password = make_password(password)
            login.save()
            return UpdateLogin(login=login)
        except Login.DoesNotExist:
            return None

class DeleteLogin(graphene.Mutation):
    success = graphene.Boolean()

    class Arguments:
        id = graphene.String(required=True)

    def mutate(self, info, id):
        try:
            login = Login.objects.get(pk=id)
            login.delete()
            return DeleteLogin(success=True)
        except Login.DoesNotExist:
            return DeleteLogin(success=False)



class LoginResponse(graphene.ObjectType):
    success = graphene.Boolean()
    message = graphene.String()
    login = graphene.Field(LoginType)

class LoginMutation(graphene.Mutation):
    class Arguments:
        phoneNum = graphene.String(required=True)
        password = graphene.String(required=True)

    Output = LoginResponse

    def mutate(self, info, phoneNum, password):
        try:
            user = Login.objects.get(phone_num=phoneNum)
            if check_password(password, user.password):
                return LoginResponse(success=True, login=user, message="Login successful")
            else:
                return LoginResponse(success=False, login=None, message="Invalid password")
        except Login.DoesNotExist:
            return LoginResponse(success=False, login=None, message="Invalid phone number")



class Query(graphene.ObjectType):
    all_logins = graphene.List(LoginType)
    login_by_id = graphene.Field(LoginType, id=graphene.Int())
    login_by_email = graphene.Field(LoginType, email=graphene.String())

    def resolve_all_logins(root, info):
        return Login.objects.all()

    def resolve_login_by_id(root, info, id):
        try:
            return Login.objects.get(pk=id)
        except Login.DoesNotExist:
            return None

    def resolve_login_by_email(root, info, email):
        try:
            return Login.objects.get(email=email)
        except Login.DoesNotExist:
            return None

class Mutation(graphene.ObjectType):
    login = LoginMutation.Field()
    create_login = CreateLogin.Field()
    update_login = UpdateLogin.Field()
    delete_login = DeleteLogin.Field()

login_schema = graphene.Schema(query=Query, mutation=Mutation)
