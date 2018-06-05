# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect, reverse
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse_lazy
from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Q, Sum, Count
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.models import User, Group
from django.db import transaction
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.conf import settings
from django.contrib.auth.views import PasswordChangeView

from bee_django_crm.models import PreUser
from bee_django_crm.exports import after_check_callback

from .decorators import cls_decorator, func_decorator
from .models import UserProfile, UserClass
from .forms import UserForm, UserProfileForm, profile_inline_formset, UserClassForm, UserGroupForm
from .utils import get_max_student_id


# Create your views here.
def test(request):
    # user = User.objects.create_user(username='test3', password='a1234567')
    # user.first_name = '客服'
    # user.save()
    # UserProfile.fix_cc_room_id()

    return


def home_page(request):
    return render(request, 'bee_django_user/home_page.html')


# ========user 学生===========
@method_decorator(cls_decorator(cls_name='UserList'), name='dispatch')
@method_decorator(permission_required('bee_django_user.can_manage'), name='dispatch')
class UserList(ListView):
    model = User
    template_name = 'bee_django_user/user/list.html'
    context_object_name = 'user_list'
    paginate_by = 20

    def get_queryset(self):
        if self.request.user.has_perm("bee_django_user.view_all_users"):
            return User.objects.all().order_by('id')
        elif self.request.user.has_perm("bee_django_user.view_teach_users"):
            return User.objects.filter(userprofile__user_class__assistant=self.request.user).order_by('id')
        return []



@method_decorator(cls_decorator(cls_name='UserDetail'), name='dispatch')
class UserDetail(DetailView):
    model = User
    template_name = 'bee_django_user/user/detail.html'
    context_object_name = 'user'


@method_decorator(cls_decorator(cls_name='UserCreate'), name='dispatch')
class UserCreate(TemplateView):
    # model = User
    # form_class = UserCreateForm
    template_name = 'bee_django_user/user/create.html'
    # success_url = reverse_lazy('bee_django_user:user_list')

    # def get_context_data(self, **kwargs):
    #     context = super(UserCreate, self).get_context_data(**kwargs)
    #     context["preuser"] = PreUser.objects.get(id=self.kwargs["preuser_id"])
    #     return context

    @transaction.atomic
    def get(self, request, *args, **kwargs):
        # print(self.kwargs)
        preuser_id = request.GET["preuser_id"]
        preuser_contract_id = request.GET["preuser_contract_id"]
        if not self.request.user.has_perm('bee_django_user.add_userprofile'):
            messages.error(self.request, '没有权限')
            return redirect(reverse('bee_django_crm:preuser_contract_detail', kwargs={"pk": preuser_contract_id}))
        preuser = PreUser.objects.get(id=preuser_id)
        try:
            preuser.userprofile
        except UserProfile.DoesNotExist:
            try:
                max_student_id = get_max_student_id()
                user_profile = UserProfile()
                user_profile.preuser = preuser
                user_profile.student_id = max_student_id + 1
                if settings.COURSE_VIDEO_PROVIDER_NAME == 'cc':
                    from bee_django_course.cc import create_room
                    room_id = create_room(preuser.name + '的直播间')
                    user_profile.room_id = room_id
                user_profile.save()
                res, msg = after_check_callback(preuser_contract_id)
                messages.success(self.request, '添加用户成功')
            except Exception as e:
                print(e)
                messages.error(self.request, '发生错误')
        else:
            res, msg = after_check_callback(preuser_contract_id)
            messages.success(self.request, '已添加过用户，后续操作成功')
        return redirect(reverse('bee_django_crm:preuser_all_contract_list'))


@method_decorator(cls_decorator(cls_name='UserUpdate'), name='dispatch')
# @method_decorator(permission_required("change_user"), name='dispatch')
class UserUpdate(UpdateView):
    model = User
    form_class = UserForm
    template_name = 'bee_django_user/user/form.html'

    def get_success_url(self):
        return reverse_lazy("bee_django_user:user_detail", kwargs=self.kwargs)

    def get_context_data(self, **kwargs):
        context = super(UserUpdate, self).get_context_data(**kwargs)
        context["formset"] = profile_inline_formset(instance=self.object)
        return context

    @transaction.atomic
    def form_valid(self, form):
        if not self.request.user.has_perm('bee_django_user.change_userprofile'):
            messages.error(self.request, '没有权限')
            return redirect(reverse('bee_django_user:user_update', kwargs=self.kwargs))
        formset = profile_inline_formset(self.request.POST, instance=self.object)
        if formset.is_valid():
            profile = formset.cleaned_data[0]
            # room_id = profile['room_id']
            # self.object.userprofile.room_id = room_id
            self.object.userprofile.save()
            messages.success(self.request, '修改成功')
        return super(UserUpdate, self).form_valid(form)


@method_decorator(cls_decorator(cls_name='UserUpdate'), name='dispatch')
class UserGroupUpdate(UpdateView):
    model = User
    form_class = UserGroupForm
    template_name = 'bee_django_user/group/user_group_form.html'

    def get_success_url(self):
        return reverse_lazy("bee_django_user:user_detail", kwargs=self.kwargs)


class UserPasswordChangeView(PasswordChangeView):
    success_url = reverse_lazy('bee_django_user:user_password_change_done')
    template_name = 'bee_django_user/user/password_change.html'


    # def get_context_data(self, **kwargs):
    #     context = super(UserUpdate, self).get_context_data(**kwargs)
    #     context["formset"] = profile_inline_formset(instance=self.object)
    #     return context
    #
    # @transaction.atomic
    # def form_valid(self, form):
    #     if not self.request.user.has_perm('bee_django_user.can_change'):
    #         messages.error(self.request, '没有权限')
    #         return redirect(reverse('bee_django_user:user_update', kwargs=self.kwargs))
    #     formset = profile_inline_formset(self.request.POST, instance=self.object)
    #     if formset.is_valid():
    #         profile = formset.cleaned_data[0]
    #         # room_id = profile['room_id']
    #         # self.object.userprofile.room_id = room_id
    #         # self.object.userprofile.save()
    #         messages.success(self.request, '修改成功')
    #     return super(UserUpdate, self).form_valid(form)


# 用户组权限
@method_decorator(cls_decorator(cls_name='GroupList'), name='dispatch')
class GroupList(ListView):
    model = Group
    template_name = 'bee_django_user/group/list.html'
    context_object_name = 'group_list'
    paginate_by = 20


# ========class 班级===========
@method_decorator(cls_decorator(cls_name='ClassList'), name='dispatch')
class ClassList(ListView):
    model = UserClass
    template_name = 'bee_django_user/class/list.html'
    context_object_name = 'class_list'
    paginate_by = 20

    def get_queryset(self):
        if self.request.user.has_perm("bee_django_user.view_all_classes"):
            return UserClass.objects.all()
        if self.request.user.has_perm("bee_django_user.view_teach_classes"):
            return UserClass.objects.filter(assistant=self.request.user)
        return []


@method_decorator(cls_decorator(cls_name='ClassDetail'), name='dispatch')
class ClassDetail(DetailView):
    model = UserClass
    template_name = 'bee_django_user/class/detail.html'
    context_object_name = 'class'


@method_decorator(cls_decorator(cls_name='ClassCreate'), name='dispatch')
class ClassCreate(CreateView):
    model = UserClass
    form_class = UserClassForm
    template_name = 'bee_django_user/class/form.html'
    success_url = reverse_lazy('bee_django_user:class_list')


@method_decorator(cls_decorator(cls_name='ClassUpdate'), name='dispatch')
class ClassUpdate(UpdateView):
    model = UserClass
    form_class = UserClassForm
    template_name = 'bee_django_user/class/form.html'
    success_url = reverse_lazy('bee_django_user:class_list')

    @transaction.atomic
    def form_valid(self, form):
        if not self.request.user.has_perm('change_userclass'):
            messages.error(self.request, '没有权限')
            return redirect(reverse('bee_django_user:class_update', kwargs=self.kwargs))
        return super(ClassUpdate, self).form_valid(form)

        #
        # def get_context_data(self, **kwargs):
        #     context = super(UserUpdate, self).get_context_data(**kwargs)
        #     context["formset"] = profile_inline_formset(instance=self.object)
        #     return context
        #
        # @transaction.atomic
        # def form_valid(self, form):
        #     formset = profile_inline_formset(self.request.POST, instance=self.object)
        #     if formset.is_valid():
        #         profile = formset.cleaned_data[0]
        #         room_id = profile['room_id']
        #         self.object.userprofile.room_id = room_id
        #         self.object.userprofile.save()
        #     return super(UserUpdate, self).form_valid(form)
