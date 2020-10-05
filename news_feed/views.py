from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from .models import *
from itertools import chain
from django.db.models import Q
from datetime import timedelta
import json
import datetime
# from django.utils.datastructures import MultiValueDictKeyError
# from model_utils.managers import InheritanceManager

global news_feed_url
news_feed_url = '/'

def home(request):	

	section = request.GET.get("section", 0)
	if not section:
		if request.user.is_authenticated:
			section = request.user.profile.newsfeedsettings.defaultsection
		else:
			section = "popular"

	if section == "subscriptions" and request.user.is_authenticated:
		articles = generate_subscriptions_articles(request.user)
	elif section == "new":
		articles = generate_new_articles(request.user)
	elif section == "hot":
		articles = generate_hot_articles(request.user) 
	elif section == "best":
		articles = generate_best_articles(request.user) 
	elif section == "reacted" and request.user.is_authenticated:
		articles = generate_reacted_articles(request.user)
	elif section == "viewed" and request.user.is_authenticated:
		articles = generate_viewed_articles(request.user) 
	elif section == "self_articles" and request.user.is_authenticated:
		articles = generate_self_articles(request.user) 
	else:
		articles = []

	articles = [article for article in articles if article.can_see_article(request.user)]
	context = {
		'articles': articles,
		'section': section
	}
	return render(request, 'news_feed/index.html', context)

def generate_subscriptions_articles(user):
	if user.profile.newsfeedsettings.showviewed:
		personal_in_community_articles = PersonalInCommunityArticle.objects.filter((Q(group__in=user.groups_subs.all()) | Q(group__in=user.groups_editors.all()) | Q(group__in=user.groups_admins.all())), allowed=True)
		community_articles = CommunityArticle.objects.filter(Q(group__in=user.groups_subs.all(), allowed=True) | Q(group__in=user.groups_admins.all(), allowed=True))
	else:
		personal_in_community_articles = PersonalInCommunityArticle.objects.filter((Q(group__in=user.groups_subs.all()) | Q(group__in=user.groups_editors.all()) | Q(group__in=user.groups_admins.all())) & ~Q(views__in=[user]) & Q(allowed=True))
		community_articles = CommunityArticle.objects.filter((Q(group__in=user.groups_subs.all()) | Q(group__in=user.groups_admins.all()) | Q(group__in=user.groups_editors.all())) & ~Q(views__in=[user]) & Q(allowed=True))

	articles = sorted(chain(personal_in_community_articles, community_articles), key=lambda instance: instance.pubdate, reverse=True)
	return articles

def generate_hot_articles(user):
	news_feed = NewsFeedArticlesList.objects.get(list_type='hot')
	if not user.is_authenticated or user.profile.newsfeedsettings.showviewed:
		articles = news_feed.articles.select_subclasses().order_by('-rating')
	else:
		articles = news_feed.articles.filter(~Q(views__in=[user])).select_subclasses().order_by('-rating')
	return articles

def generate_best_articles(user):
	news_feed = NewsFeedArticlesList.objects.get(list_type='best')
	if not user.is_authenticated or user.profile.newsfeedsettings.showviewed:
		articles = news_feed.articles.select_subclasses().order_by('-rating')
	else:
		articles = news_feed.articles.filter(~Q(views__in=[user])).select_subclasses().order_by('-rating')
	return articles

def generate_new_articles(user):
	if not user.is_authenticated or user.profile.newsfeedsettings.showviewed:
		articles = BasicArticle.objects.filter(allowed=True).order_by('-pubdate').select_subclasses()
	else:
		articles = BasicArticle.objects.filter(Q(allowed=True) & ~Q(views__in=[user])).order_by('-pubdate').select_subclasses()
	return articles

def generate_reacted_articles(user):
	if user.is_authenticated:
		return BasicArticle.objects.filter(Q(allowed=True) & (Q(pluses__in=[user]) | Q(minuses__in=[user]))).order_by('-pubdate').select_subclasses()
	else:
		return HttpResponseRedirect('/')

def generate_self_articles(user):
	return BasicArticle.objects.filter(author=user).select_subclasses()

def view_article(request, articleid):
	if BasicArticle.objects.filter(id=articleid).exists():
		article = BasicArticle.objects.get(id=articleid).get_child()
		context = {
			'post': article,
		}
		return render(request, 'news_feed/aero/news_feed_article.html', context)
	else:
		return render(request, 'news_feed/aero/news_feed_article_404.html')

def manage_settings(request):
	if not request.user.is_authenticated:
		return HttpResponse('Error')
	request.user.profile.last_online_update()

	if request.POST.get('action') == 'set_default_section':
		request.user.profile.newsfeedsettings.defaultsection = request.POST.get('section', 'popular')
		request.user.profile.newsfeedsettings.save()
		return HttpResponse('Ok')

	if request.POST.get('action') == 'switch_show_viewed_settings':
		request.user.profile.newsfeedsettings.showviewed = not request.user.profile.newsfeedsettings.showviewed
		request.user.profile.newsfeedsettings.save()
		return HttpResponse('Ok')

def manage_articles(request):
	if not request.user.is_authenticated:
		return HttpResponse('Error')

	request.user.profile.last_online_update()

	if request.POST.get('action') == 'get_post': 
		articleid = request.POST.get('articleid')
		if not BasicArticle.objects.filter(id=articleid).exists():
			return HttpResponse('Error')
		else:
			article = BasicArticle.objects.get(id=articleid).get_child()

		data = {
			'text': article.text,
			'allow_comments': 'true' if article.allow_comments else 'false',
			}
		return HttpResponse(json.dumps(data))

	elif request.POST.get('action') == 'plus_minus':
		if BasicArticle.objects.filter(id=request.POST.get('articleid')):
			article = BasicArticle.objects.get(id=request.POST.get('articleid')).get_child()
			if not article.can_plus_or_comment(request.user):
				return HttpResponse('Error')
		else:
			return HttpResponse('Error')

		if article.can_plus_or_comment(request.user):
			if request.POST.get('type') == 'plus' or request.POST.get('type') == 'plusplus':			
				article.plus(request.user)
			elif request.POST.get('type') == 'remove_plus':
				article.remove_plus(request.user)
			elif request.POST.get('type') == 'minus' or request.POST.get('type') == 'minusminus':
				article.minus(request.user)
			elif request.POST.get('type') == 'remove_minus':
				article.remove_minus(request.user)

		return HttpResponse('Ok')

	elif request.POST.get('action') == 'mark_viewed':
		articleid = request.POST.get('articleid')
		if not BasicArticle.objects.filter(id=articleid).exists():
			return HttpResponse('Error')
		else:
			article = BasicArticle.objects.get(id=articleid).get_child()

		if article.can_see_article(request.user):
			value = request.POST.get('value')
			value = True if value == 'true' else False

			if value and request.user not in article.views.all():
				article.views.add(request.user)
				article.save()
			elif (not value) and request.user in article.views.all():
				article.views.remove(request.user)
				article.save()				
			return HttpResponse('Ok')
		return HttpResponse('Error')

	elif request.POST.get('action') == 'create_personal_article':
		allow_comments = True if request.POST.get('allow_comments') == 'on' else False

		if request.POST.get("text", ''):
			new_article = PersonalArticle(author=request.user, text=request.POST.get("text"), allow_comments=allow_comments)	
			new_article.save()

			for file in request.FILES.getlist('files'):
				if file.content_type in ['image/png', 'image/jpeg', 'application/pdf', 'text/plain', 'application/msword'] and file.size <= 5000000:					
					new_file = BasicArticleFile(name=file.name.replace("'", "").replace('"', ''), file=file, files_list=new_article.files)
					new_file.save()

		return HttpResponseRedirect(request.POST.get('return_url', news_feed_url))

	elif request.POST.get('action') == 'create_community_article':
		personal = True if request.POST.get('personal') == 'on' else False
		allow_comments = True if request.POST.get('allow_comments') == 'on' else False

		groupid = request.POST.get('groupid') 
		group = Group.objects.get(id=groupid)

		if request.user in group.editors.all() or request.user == group.admin or group.allowarticles == 1 or group.allowarticles == 2:
			if request.POST.get("text", ''):
				if personal:
					new_article = PersonalInCommunityArticle(group=group, author=request.user, text=request.POST.get("text"), allow_comments=allow_comments)	
				else:
					new_article = CommunityArticle(group=group, text=request.POST.get("text"), allow_comments=allow_comments)	

				if group.allowarticles == 2 and not (request.user in group.editors.all() or request.user == group.admin):	
					new_article.allowed = False	
				new_article.save()

				for file in request.FILES.getlist('files'):
					if file.content_type in ['image/png', 'image/jpeg', 'application/pdf', 'text/plain', 'application/msword'] and file.size <= 5000000:					
						new_file = BasicArticleFile(name=file.name.replace("'", "").replace('"', ''), file=file, files_list=new_article.files)
						new_file.save()

		slug = group.slug
		return HttpResponseRedirect('/groups/' + str(slug) + '/')

	elif request.POST.get('action') == 'edit_article': 
		articleid = request.POST.get('articleid')
		
		if not BasicArticle.objects.filter(id=articleid).exists():
			return HttpResponse('Error')
		else:
			article = BasicArticle.objects.get_subclass(id=articleid)

		if not article.can_edit_article(request.user):
			return False

		if not request.POST.get("text", ''):
			return False

		allow_comments = True if request.POST.get('allow_comments') == 'on' else False
		article.allow_comments = allow_comments
		article.text = request.POST.get("text")
		article.save()

		for fileid in request.POST.get("removedfiles").split():
			try:
				file = article.files.get(id=int(fileid))
				file.delete()
			except:
				pass
		
		for file in request.FILES.getlist('files'):
			if file.content_type in ['image/png', 'image/jpeg', 'application/pdf', 'text/plain', 'application/msword'] and file.size <= 5000000:
				new_file = BasicArticleFile(files_list=article.files, name=file.name.replace("'", "").replace('"', ''), file=file)
				new_file.save()

		return HttpResponseRedirect(request.POST.get('return_url'))

	elif request.POST.get('action') == 'delete_article': 
		articleid = request.POST.get('articleid')
		article = BasicArticle.objects.get_subclass(id=articleid)

		if article.has_rights(request.user):
			article.delete()

		return HttpResponse('Ok')


def manage_comments(request):
	if not request.user.is_authenticated:
		return HttpResponse('Error')

	if request.POST.get('action') == 'plus_minus':
		if BasicComment.objects.filter(id=request.POST.get('commentid')):
			comment = BasicComment.objects.get(id=request.POST.get('commentid'))
			if not comment.comments_list.article.get_child().can_comment_article(request.user) or not comment.comments_list.article.get_child().can_see_article(request.user):
				return HttpResponse('Error')
		else:
			return HttpResponse('Error')

		if request.POST.get('type') == 'plus' or request.POST.get('type') == 'plusplus':			
			comment.plus(request.user)
		elif request.POST.get('type') == 'remove_plus':
			comment.remove_plus(request.user)
		elif request.POST.get('type') == 'minus' or request.POST.get('type') == 'minusminus':
			comment.minus(request.user)
		elif request.POST.get('type') == 'remove_minus':
			comment.remove_minus(request.user)

		return HttpResponse('Ok')

	elif request.POST.get('action') == 'create_comment':

		articleid = request.POST.get('articleid')
		if not BasicArticle.objects.filter(id=articleid).exists():
			return HttpResponse('Error')
		else:
			article = BasicArticle.objects.get(id=articleid).get_child()

		if not article.allow_comments:
			return HttpResponse('Error')

		if article.__class__.__name__ != 'PersonalArticle':
			group = article.group
			if not group.can_see_group(request.user):
				return HttpResponse('Error')

		comment_text = request.POST.get('text')
		if comment_text.replace(' ', '').rstrip() == '':
			return HttpResponse('empty')
		if len(comment_text) > 750:
			return HttpResponse('long')

		new_comment = BasicComment(author=request.user, text=comment_text, comments_list=article.comments)
		new_comment.save()

		data = {
			'avatar': '/media/' + str(request.user.profile.avatar),
			'text': comment_text,
			'author': request.user.username,
			'pubdate': str(new_comment.pubdate),
			'postid': article.id,
			'commentid': new_comment.id,
			'locationid': 'post' + str(articleid) + 'comments',
			'parentname': ''		
		}

		replycommentid = request.POST.get('reply')
		if replycommentid != '' and BasicComment.objects.filter(id=int(replycommentid)).exists():				
			replycomment = BasicComment.objects.get(id=int(replycommentid))
			replyuser = replycomment.author
			new_comment.replyto = replyuser
			if not replycomment.parent:
				new_comment.parent = replycomment
				new_comment.save()
			else:
				new_comment.parent = replycomment.parent
				new_comment.save()					

			data['locationid'] = 'comment' + str(new_comment.parent.id) + 'children'
			data['parentname'] = replyuser.username

		request.user.profile.last_online_update()
		return HttpResponse(json.dumps(data))

	elif request.POST.get('action') == 'delete_comment':

		commentid = request.POST.get('commentid')
		if not BasicComment.objects.filter(id=commentid).exists():
			return HttpResponse('Error')
		else:
			comment = BasicComment.objects.get(id=commentid)

		article = comment.comments_list.article.get_child()

		if not article.allow_comments:
			return HttpResponse('Error')

		if article.__class__.__name__ != 'PersonalArticle':
			group = article.group
			if not group.can_see_group(request.user):
				return HttpResponse('Error')
	
		if request.user == comment.author:
			if comment.childrencomments.all():
				comment.is_deleted = True
				comment.save()
				return HttpResponse('is_deleted')
			else:
				if comment.parent and comment.parent.is_deleted and comment.parent.childrencomments.count() == 1:
					comment.parent.delete()
				else:
					comment.delete()
			request.user.profile.last_online_update()
			return HttpResponse('Ok')
		return HttpResponse('Error')

	elif request.POST.get('action') == 'edit_comment':
		commentid = request.POST.get('commentid')
		if not BasicComment.objects.filter(id=commentid).exists():
			return HttpResponse('Error')
		else:
			comment = BasicComment.objects.get(id=commentid)

		article = comment.comments_list.article.get_child()

		if not article.allow_comments:
			return HttpResponse('Error')

		if article.__class__.__name__ != 'PersonalArticle':
			group = article.group
			if not group.can_see_group(request.user):
				return HttpResponse('Error')

		if request.user == comment.author:			
			commenttext = request.POST.get('text')
			if commenttext.replace(' ', '').rstrip() == '':
				return HttpResponse('empty')
			if len(commenttext) > 750:
				return HttpResponse('long')
			comment.text = commenttext
			comment.save()
			
			request.user.profile.last_online_update()
			return HttpResponse('Ok')
		return HttpResponse('Error')
	return HttpResponse('Ok')