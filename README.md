# Django PubSubPull #

`django-pubsubpull` is intended to help you decouple micro-services. It provides mechanisms that allow services to publish changes, subscribe to change notifications, and pull records.

In practice what we'll end up with is along the lines of:

* Use Django slumber and async to provide a load of basic infrastructure this is going to need.
* Provide new models for tracking database level changes to certain tables (models), and database triggers to ensure that they are properly recorded.
* All operations will be based on HTTP using GET, PUT and DELETE only.
* Django middleware to capture as much information about the request and the underlying changes we can and to tie that in to the records of database changes recorded there.
* Support for Django 1.0 through 1.7. We may support 1.8 and later if we can make our middleware subsume the functionality of the old transaction middleware.
* Only support Postgres 9.4 and later.

The use cases we envisage include:

* A service needs to locally cache a copy of some attributes of an object held in another micro-service, generally for performance reasons (for example, a billing service needing copies of a customer's location so that it can choose the correct rates).
* A service needs to record meta-data about user instructed changes for audit trail purposes (for example, any change to a customer email subscription is recorded with full details of who made the change and when it was made).
* A service needs to be notified of certain API calls so that it can in turn trigger other behaviours (for example, a comms service sending a welcome email when a new user is created).

The three parts are:

* Publish: A service will notify it's subscribers about any changes to the requested model instances. Ultimately the publish will hook into a database trigger to ensure that changes are always properly recorded no matter how it occurs.
* Subscribe: A service can request change notifications be sent to it from the publishing service. The subscriber is able to specify a URL that is used for a PUT request when changes are notified.
* Pull: A service can iterate over all of the instances of a particular model and then periodically iterate over new ones.

