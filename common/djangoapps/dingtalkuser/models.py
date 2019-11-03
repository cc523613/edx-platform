# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from config_models.models import ConfigurationModel

# Create your models here.

class DingtalkUserconfig(ConfigurationModel):

    key = models.TextField(blank=True, verbose_name="Client ID")
    secret = models.TextField(blank=True, verbose_name="Client Secret")

    class Meta:
        app_label = "dingtalkuser"
        verbose_name = "DingTalk Config(h5 page)"
        verbose_name_plural = verbose_name
        db_table = "dingtalk_user_h5_config"

    def get_setting(self, name):
        if name == "KEY":
            if self.key:
                return self.key
            return getattr(settings, 'DINGTALK_ACCESS_KEY', '')
        if name == "SECRET":
            if self.secret:
                return self.secret
            return getattr(settings, 'DINGTALK_APP_SECRET', '')
        raise KeyError
