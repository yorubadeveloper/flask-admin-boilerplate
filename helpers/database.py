from pymongo import MongoClient
import configuration

connection_params = configuration.connection_params

#connect to mongodb
# mongoconnection = MongoClient(
#     'mongodb://{user}:{password}@{host}:'
#     '{port}/{namespace}?retryWrites=false'.format(**connection_params)
# )
mongoconnection = MongoClient("localhost", 27017)


db = mongoconnection.databasename
