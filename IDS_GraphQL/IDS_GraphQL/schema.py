import graphene

from Authentication.schema import Query as AuthenticationQuery, Mutation as AuthenticationMutation
from Core.schema import Query as CoreQuery, Mutation as CoreMutation
# Import other app schemas as needed

class Query(AuthenticationQuery, CoreQuery, graphene.ObjectType):
    pass

class Mutation(AuthenticationMutation, CoreMutation, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)