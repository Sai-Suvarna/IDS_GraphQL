import graphene
import graphql_jwt
from Authentication.schema import login_schema
from Core.schema import productdetails_schema

class Query(login_schema.Query, productdetails_schema.Query, graphene.ObjectType):
    pass

class Mutation(login_schema.Mutation, productdetails_schema.Mutation, graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    verify_token = graphql_jwt.Verify.Field()    
    pass
schema = graphene.Schema(query=Query, mutation=Mutation)
