# -*- coding: utf-8 -*-  
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.core.urlresolvers import reverse
from hiveall.core.models import User, Orgnization, OrgContact
from hiveall.org.models import Team 
from django.contrib.auth.models import Permission, User as auth_user
from django.contrib.contenttypes.models import ContentType
import logging
from django.utils import simplejson

logger = logging.getLogger('hiveall.works.testcase')

class OrgViewsTest(TestCase):
    username = 'fzz23163@163.com'
    password = '123'
    email = 'fzz23163@163.com'
    
    def setUp(self):
        self.client.post('/accounts/login', {'username': self.username, 'password': self.password })
        self.django_user = auth_user.objects.get(email = self.email)
        self.core_user = self.django_user.get_profile()
        self.org, created = Orgnization.objects.get_or_create(name = 'test_org',\
                region = u'广东|深圳|南山区', creator = self.core_user)
        if self.core_user.orgnization <> self.org:
            self.core_user.orgnization = self.org
            self.core_user.save()

        content_type, created = ContentType.objects.get_or_create(name = 'orgnization', app_label = 'core', model = 'orgnization')
        Permission.objects.get_or_create(name = 'Can manage orgnization', content_type = content_type, codename = 'manage_org_orgs')
        Permission.objects.get_or_create(name = 'Can manage orgnization invite', content_type = content_type, codename = 'manage_org_invite')
        Permission.objects.get_or_create(name = 'Can manage orgnization teams', content_type = content_type, codename = 'manage_org_teams')

            # test:你输入的email不能为空
        post_dict = dict(transfer_email='')
        response = self.client.post(reverse('org:transfer_org'), post_dict, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        return_json = u'''{"state": false, "errMsg": "你输入的email不能为空"}'''
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response._container[0],return_json)

        # 邮箱对应的用户不存在
        post_dict = dict(transfer_email='xxxuoguo6746767687897@185.com')
        return_json = u'''{"state": false, "errMsg": "邮箱对应的用户不存在"}'''
        response = self.client.post(reverse('org:transfer_org'), post_dict, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response._container[0],return_json)

        # 成功转移org等待接受
        post_dict = dict(transfer_email=self.email)
        return_json = u'''{"state": true}'''
        response = self.client.post(reverse('org:transfer_org'), post_dict, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        print response._container[0]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response._container[0],return_json)

        #test:你没有移除该机构的权限
        return_json = u'''{"state": false, "errMsg": "你没有移除该机构的权限"}'''
        org = self.core_user.orgnization
        org.creator = None
        org.save()
        response = self.client.post(reverse('org:transfer_org'),HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response._container[0],return_json)

        # 用户机构不存在
        return_json = u'''{"state": false, "errMsg": "用户机构不存在"}'''
        self.core_user.orgnization = None
        self.core_user.save()

        response = self.client.post(reverse('org:transfer_org'),HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response._container[0],return_json)

    # def test_create_team(self):
    #     logger.debug(u'-----------------------开始测试Team创建功能-----------------------')
    #     team_form = dict(name = 'test_team', details = 'Test team', orgnization = self.org)
    #     response = self.client.post(reverse('org:team_add'), team_form, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    #     self.assertEqual(response.status_code, 302)
    #     _team = Team.objects.get(name = 'test_team')
    #     self.assertNotEqual(_team.id, None)
    #
    # def test_transfer_org(self):
    #     logger.debug(u'-----------------------开始测试机构转让功能-----------------------')
    #     response = self.client.post(reverse('org:transfer_org'),
    #             dict(transfer_email = 'terry12903@126.com'), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    #     self.assertEqual(response.status_code, 200)
    #     data = simplejson.loads(response.content)
    #     self.assertEqual(data.get('state'), True)
    #     self.assertEqual(auth_user.objects.get(email = 'doodoll@163.com').get_profile().orgnization,None)
    #
    # def test_team_add_member(self):
    #     logger.debug(u'-----------------------开始测试机构添加用户功能-----------------------')
    #     team, created = Team.objects.get_or_create(name = 'test_team', details = 'Test team', orgnization = self.org)
    #     data = dict(team = team.id, members = '%s,' % self.core_user.id)
    #     response = self.client.post(reverse('org:team_add_members'), data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    #     self.assertEqual(response.status_code, 200)
    #     ret = simplejson.loads(response.content)
    #     self.assertEqual(ret.get('state'), True)
    #     teams = auth_user.objects.get(email = 'doodoll@163.com').get_profile().team_set.all()
    #     self.assertEqual(team in teams, True)
    #
    #
    # def test_kicked_user(self):
    #     logger.debug(u'-----------------------开始测试机构移除用户功能-----------------------')
    #     djangoUser, created = auth_user.objects.get_or_create(username = 'Terry', first_name = 'Xu', \
    #             last_name = 'Terry', email = 'terry12903@126.com', is_staff = False, \
    #             is_active = True, is_superuser = False, password = '!')
    #     _user, created = User.objects.get_or_create(name = 'terry12903@126.com',\
    #                     user = djangoUser, orgnization = self.org)
    #     response = self.client.post(reverse('org:kicked_user'), \
    #             dict(uids = '%s,' % (_user.id, )), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    #     self.assertEqual(response.status_code, 200)
    #     ret = simplejson.loads(response.content)
    #     self.assertEqual(ret.get('state'), True)
    #     kicked_user = User.objects.get(name = 'terry12903@126.com')
    #     self.assertEqual(kicked_user.orgnization, None)
    #
    # def test_invite_user(self):
    #     logger.debug(u'-----------------------开始测试机构邀请用户加入功能-----------------------')
    #     team, created = Team.objects.get_or_create(name = 'test_team', details = 'Test team', orgnization = self.org)
    #     data = [dict(email = 'terry12903@126.com', team_name = team.name , team_id = team.id)]
    #     #response = self.client.post(reverse('org:invite_user'), {'invite_emails': simplejson.dumps(data)}, content_type="application/json", HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    #     response = self.client.post(reverse('org:invite_user'), \
    #             {'invite_emails': simplejson.dumps(data)}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    #     self.assertEqual(response.status_code, 200)
    #     data = simplejson.loads(response.content)
    #     self.assertEqual(data.get('state'), True)
    #
    # def test_create_org(self):
    #     logger.debug(u'-----------------------开始测试机构创建功能-----------------------')
    #     # self.client.post(reverse('user_logout'))
    #     #当你测试的时候，希望将email的值重置一下， 一定是现在doodoll上没有的email
    #     registerForm = dict(email = 'XxX@126.com', screen_name = 'XxX', password = '123', confirm = '123')
    #     response = self.client.post(reverse('auth_bind_register'), registerForm)
    #     self.assertEqual(response.status_code, 200)
    #     response = self.client.post(reverse('org:create_org'), \
    #             {'name': 'testCreateOrg', 'region': 'GuangDong|SZ|NS'},HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    #     self.assertEqual(response.status_code, 302)
    #
    # def test_edit_org(self):
    #     logger.debug(u'-----------------------开始测试机构修改功能-----------------------')
    #     response = self.client.post(reverse('org:amend_org'), \
    #             dict(name = 'afterEditOrg', address = 'ShenZhen city', \
    #             phone_num = '15112368126', scale = 50 ))
    #     self.assertEqual(response.status_code, 200)
    #     after_edit_org = Orgnization.objects.get(id = self.org.id)
    #     self.assertEqual(after_edit_org.name, 'afterEditOrg')
    #     self.assertEqual(after_edit_org.orgcontact.phone_num, '15112368126')
    #
    # def test_verify_org(self):
    #    logger.debug(u'-----------------------开始测试用户是否属于该机构功能-----------------------')
    #    response = self.client.get(reverse('org:verify_org'), {'uid':self.django_user.id,'uids':None}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    #    self.assertEqual(response.status_code, 200)
    #
    # def test_user_setting(self):
    #     logger.debug(u'-----------------------开始测试显示机构成员信息功能-----------------------')
    #     response = self.client.get(reverse('user_setting', args = [self.core_user.user.id ]))
    #     self.assertEqual(response.status_code, 200)
    #
    # def test_acquire_user(self):
    #     logger.debug(u'-----------------------开始测试机构授权功能-----------------------')
    #     djangoUser, created = auth_user.objects.get_or_create(username = 'Terry', first_name = 'Xu', \
    #             last_name = 'Terry', email = 'terry12903@126.com', is_staff = False, \
    #             is_active = True, is_superuser = False, password = '!')
    #     _user, created = User.objects.get_or_create(name = 'terry12903@126.com',\
    #                     user = djangoUser, orgnization = self.org)
    #     response = self.client.post(reverse('org:org_manage'), \
    #             dict(uids = _user.id, code_name = 'manage_org_orgs'), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    #     self.assertEqual(response.status_code, 200)
    #     data = simplejson.loads(response.content)
    #     self.assertEqual(data.get('state'), True)
    #     permission = Permission.objects.get(codename = 'manage_org_orgs')
    #     perm_user = auth_user.objects.get(email = 'terry12903@126.com')
    #     self.assertEqual(permission in perm_user.user_permissions.all(), True)
    #
    # def test_multiple_login(self):
    #     logger.debug(u'-----------------------开始测试多身份登录功能-----------------------')
    #     #response = self.client.post('/accounts/login', {'username': self.username, 'password': self.password })
    #     #self.assertRedirects(response, reverse('core_multiple_roles'))
    #     response = self.client.get(reverse('org:verify_org'),{'uid':self.django_user.id,'uids':None}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    #     self.assertEqual(response.status_code, 200)
    #
    # # commented by suxiaoming 2014-08-12
    # # def test_register(self):
    # """only the first time would succeed"""
    # #     logger.debug(u'-----------------------开始测试注册功能-----------------------')
    # #     #当你测试的时候，希望将email的值重置一下， 一定是现在doodoll上没有的email
    # #     registerForm = dict(email = 'nofzz@126.com', screen_name = 'nofzz', password = '123', confirm = '123')
    # #     response = self.client.post(reverse('auth_bind_register'), registerForm)
    # #     self.assertEqual(response.status_code, 200)
    # #     self.assertNotEqual(auth_user.objects.get(email = 'nofzz@126.com').email, None)
    # #~ commented by suxiaoming

    def tearDown(self):
        pass
