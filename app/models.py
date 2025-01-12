from .extensions import db
from sqlalchemy import Index
from flask_admin.contrib.sqla import ModelView
from .config import Config
from sqlalchemy.sql import func
from wtforms.validators import email, Regexp, DataRequired
from wtforms_alchemy import Unique
from datetime import datetime

class client(db.Model):
    __table_name__ = 'clients'
    #__tableargs__ = (Index('name_idx', 'name', unique=True))
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255),nullable=False)
    contact = db.Column(db.String(255),nullable=False)
    emailaddress = db.Column(db.String(255),nullable=False)
    description = db.Column(db.Text)
    squidconfig=db.relationship('squidconfig', back_populates='client')
    editing_date = db.Column(db.DateTime, default=datetime.now(),onupdate=datetime.now())

    def __repr__(self):
        return self.name 

class environment(db.Model): 
    __table_name__ = 'environments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255),nullable=False)
    vipaddress = db.Column(db.String(100))
    description = db.Column(db.Text)
    squidconfig=db.relationship('squidconfig', back_populates='environment')
    squidport=db.relationship('squidport', back_populates='environment')

    def __repr__(self):
        return self.name

class squidconfig(db.Model):
    __table_name__ = 'squidconfig'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255),nullable=False)
    description = db.Column(db.Text)
    client_id= db.Column(db.Integer,db.ForeignKey(client.id))
    client=db.relationship("client", back_populates="squidconfig")
    environment_id= db.Column(db.Integer,db.ForeignKey(environment.id))
    environment = db.relationship("environment", back_populates="squidconfig")
    cachepeer = db.relationship("cachepeer", back_populates="squidconfig")
    squidsource = db.relationship("squidsource", back_populates="squidconfig")
    dest_host = db.relationship("dest_host", back_populates="squidconfig")
    dest_url = db.relationship("dest_url", back_populates="squidconfig")

    def __repr__(self):
        return self.name

class squidport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    interface = db.Column(db.Integer, default=1)
    port = db.Column(db.Integer)
    reverse = db.Column(db.Boolean, default=False)
    options = db.Column(db.String(255))
    certificate = db.Column(db.String(255))
    environment_id= db.Column(db.Integer,db.ForeignKey(environment.id))
    environment = db.relationship("environment", back_populates="squidport")

    def __repr__(self):
        return self.port

class cachepeer(db.Model):
    __table_name__ = 'cachepeer'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255),nullable=False)
    destination = db.Column(db.String(100),nullable=False)
    destination_port = db.Column(db.Integer)
    options = db.Column(db.String(255))
    description = db.Column(db.Text)
    squidconfig_id = db.Column(db.Integer,db.ForeignKey(squidconfig.id))
    squidconfig = db.relationship("squidconfig", back_populates="cachepeer")

    def __repr__(self):
        return self.name

class squidsource(db.Model):
    __table_name__ = 'squidsource'
    id = db.Column(db.Integer, primary_key=True)
    squidconfig_id = db.Column(db.Integer,db.ForeignKey(squidconfig.id))
    squidconfig = db.relationship("squidconfig", back_populates="squidsource")
    ipaddress = db.Column(db.String(16),nullable=False)

    def __repr__(self):
        return self.ipaddress

class dest_host(db.Model):
    __table_name__ = 'dest_host'
    id = db.Column(db.Integer, primary_key=True)
    squidconfig_id = db.Column(db.Integer,db.ForeignKey(squidconfig.id))
    squidconfig = db.relationship("squidconfig", back_populates="dest_host")
    destination = db.Column(db.String(255),nullable=False)

    def __repr__(self):
        return self.destination

class dest_url(db.Model):
    __table_name__ = 'dest_url'
    id = db.Column(db.Integer, primary_key=True)
    squidconfig_id = db.Column(db.Integer,db.ForeignKey(squidconfig.id))
    squidconfig = db.relationship("squidconfig", back_populates="dest_url")
    destination = db.Column(db.String(255),nullable=False)

    def __repr__(self):
        return self.destination


class clientview(ModelView):
    can_export = True
    form_columns = ['name', 'contact','emailaddress','description']
    column_labels = dict(name='Naam',contact='Contactpersoon',emailaddress='Mailadres',description='Omschrijving')
    form_args = {
        'name': { 'label': 'Naam','validators': [Unique(client.name, message='Naam bestaat al')] },
        'emailaddress': { 'label' : 'Mailadres','validators': [email(message='Geen geldig mail adres')] },
        'description': { 'label': 'Omschrijving'}
        }

class squidportview(ModelView):
    can_export = True
    form_columns = ['interface', 'port','reverse','options','certificate','environment']
    column_labels = dict(interface='Interface',port='port',reverse='Reverse proxy',options='Opties', certificate='SSL certificaat', environment='Omgeving')
    form_args = {
        'interface': { 'label': 'Interface nummer (start bij 0)'},
        'port': { 'label' : 'TCP Poort'},
        'reverse': { 'label': 'Reverse proxy'},
        'options': { 'label': 'Extra opties' },
        'certificate': { 'label': 'SSL certificaat' },
        'environment': { 'label': 'Squid omgeving' }
        }

class environmentview(ModelView):
    can_export = True
    form_columns = ['name','vipaddress','description']
    column_labels = dict(name='Naam',vipaddress='VIP adres',description='Omschrijving')
    form_args = {
        'name': { 'label': 'Naam', 'validators': [Regexp('^[0-9a-zA-Z_]+$',message='Alleen letters, cijfers en _ toegestaan'), Unique(environment.name, message='Naam bestaat al')] },
        'vipaddress': { 'label': 'VIP adres', 'validators': [Regexp('^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$',message='Fout IP adres')] },
        'description': { 'label': 'Omschrijving'}
        }

class squidconfigview(ModelView):
    can_export = True
    form_columns = ['name', 'client', 'environment', 'description']
    column_labels = dict(name='Naam',client='Klant',environment='Squid omgeving',description='Omschrijving')
    form_args = {
        'name': { 'label': 'Naam', 'validators': [Regexp('^[0-9a-zA-Z_]+$',message='Alleen letters, cijfers en _ toegestaan'),Unique(squidconfig.name, message='Naam bestaat al')] },
        'client': { 'label': 'Klant' },
        'environment': { 'label': 'Omgeving' },
        'description': { 'label': 'Omschrijving'}
        }

class cachepeerview(ModelView):
    can_export = True
    form_columns = ['name', 'destination', 'destination_port', 'options', 'squidconfig', 'description']
    column_labels = dict(name='Naam',destination='Doel',destination_port='Doel poort', options='Opties', squidconfig='Squid configuratie', description='Omschrijving')
    form_args = {
        'name': { 'label': 'Naam', 'validators': [Regexp('^[0-9a-zA-Z_]+$',message='Alleen letters, cijfers en _ toegestaan'),Unique(cachepeer.name, message='Naam bestaat al')] },
        'destination': { 'label': 'Doel' },
        'destination_port': { 'label': 'Doel poort' },
        'options': { 'label': 'Opties' },
        'squidconfig': { 'label': 'Squid configuratie' },
        'description': { 'label': 'Omschrijving'}
        }

class squidsourceview(ModelView):
    can_export = True
    form_columns = ['squidconfig', 'ipaddress']
    column_labels = dict(squidconfig='Squid configuratie', ipaddr='IP Adres')
    form_args = {
        'ipaddress': { 'label': 'Bron IP adres', 'validators': [Regexp('^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$',message='Fout IP adres')] },
        'squidconfig': { 'label': 'Squid configuratie' }
        }

class dest_hostview(ModelView):
    can_export = True
    form_columns = ['squidconfig', 'destination']
    column_labels = dict(squidconfig='Squid configuratie', destination='Destination hostnaam')
    form_args = {
        'destination': { 'label': 'Destination hostnaam', 'validators': [Regexp('^[0-9a-zA-Z_\.]+$',message='Alleen letters, cijfers, punten en _ toegestaan')] },
        'squidconfig': { 'label': 'Squid configuratie' }
        }

class dest_urlview(ModelView):
    can_export = True
    form_columns = ['squidconfig', 'destination']
    column_labels = dict(squidconfig='Squid configuratie', destination='Destination URL regex')
    form_args = {
        'destination': { 'label': 'Destination URL'},
        'squidconfig': { 'label': 'Squid configuratie' }
        }
