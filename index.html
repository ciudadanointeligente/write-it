---
layout: page
exclude: true
---

{% assign index_page_html = null %}
{% capture index_page_html %}
	{% for p in paginator.posts %}
		<div class="ghpb-post">
			<div class="well ghpb-well-outline">
				{% if p.title %}
					<h2><a href="{{ site.url }}{{ p.url }}">{{ p.title }}</a></h2>
				{% else %}
					<h2><a href="{{ site.url }}{{ p.url }}">{{ site.description }}</a></h2>
				{% endif %}
				{% if p.subtitle %}
					<h4>{{ p.subtitle }}</h4>
				{% endif %}

				{% if p.alert or p.notice %}
					<br>
					{% if p.alert %}
					<div class="alert alert-block">
						{{ p.alert }}
					</div>
					{% endif %}

					{% if p.notice %}
					<div class="alert alert-block alert-success">
						{{ p.notice }}
					</div>
					{% endif %}
				{% endif %}

				<br>
				{{ p.content }}

				<br>
				<div class="row">
					<small>
						<div class="span3 offset1">
							{% if site.font_awesome.enabled %}
								<i class="icon-user"></i> 
							{% endif %}
							Authored by 
							{% if p.author %}
								{{ p.author }}.
							{% else %}
								{{ site.author }}.
							{% endif %}
							<br>

							{% if site.font_awesome.enabled %}
								<i class="icon-pencil"></i> 
							{% endif %}
							Published on {{ p.date | date_to_long_string }}.
							<br>

							{% assign enable_disqus_show_comments = false %}
							{% if site.disqus.enabled and site.disqus.show_comment_count and p.disqus == null %}
								{% assign enable_disqus_show_comments = true %}
							{% elsif site.disqus.enabled and site.disqus.show_comment_count and p.disqus.enabled == null %}
								{% assign enable_disqus_show_comments = true %}
							{% elsif site.disqus.enabled and site.disqus.show_comment_count and p.disqus.enabled %}
								{% assign enable_disqus_show_comments = true %}
							{% endif %}

							{% if enable_disqus_show_comments %}
								{% if site.font_awesome.enabled %}
									<i class="icon-comments"></i> 
								{% endif %}
								<a href="{{ site.url }}{{ p.url }}#disqus_thread">Comments</a>
								<br>
							{% endif %}
						</div>

						<div class="span3">
							{% if p.category.size > 0 %}
								{% if site.font_awesome.enabled %}
									<i class="icon-folder-open"></i> 
								{% endif %}
								Category: 
								<a href="{{ site.url }}/filter.html?category={{ p.category | replace: ' ', '___' | downcase }}">
									{{ p.category | capitalize }}
								</a>
								<br>
							{% endif %}

							{% if p.tags.size > 0 %}
								{% assign index_post_tag_names = null %}
								{% capture index_post_tag_names %}
									{% for index_post_t in p.tags %}
										{{ index_post_t | replace: ' ', '___' }}
									{% endfor %}
								{% endcapture %}

								{% capture index_post_sorted_tag_names %}
									{{ index_post_tag_names | split:' ' | sort | join:' ' }}
								{% endcapture %}

								{% capture index_post_number_of_tags %}
									{{ index_post_sorted_tag_names | number_of_words }}
								{% endcapture %}

								{% if site.font_awesome.enabled %}
									<i class="icon-tags"></i> 
								{% endif %}
								Tags: 
								{% assign index_post_first_tag = true %}
								{% assign index_post_prev_tag = '' %}
								{% for index_post_i in (1..index_post_number_of_tags) %}
									{% capture index_post_tag %}{{ index_post_sorted_tag_names | truncatewords:index_post_i | remove:'...' | split:' ' | last | downcase }}{% endcapture %}
									{% if index_post_prev_tag != index_post_tag %}
										{% if index_post_first_tag %}
											{% assign index_post_first_tag = false %}
										{% else %}
											, 
										{% endif %}
										{% assign index_post_prev_tag = index_post_tag %}
										<a href="{{ site.url }}/filter.html?tag={{ index_post_tag }}">{{ index_post_tag | replace: '___', ' ' }}</a>
									{% endif %}
								{% endfor %}
							{% endif %}
						</div>
					</small>
				</div>
			</div>
		</div>
		<br>
		<br>
	{% endfor %}

	<div class="pagination">
		<div class="row">
			<div class="span2 offset1">
				{% if paginator.previous_page %}
					{% if paginator.previous_page == 1 %}
						<a href="{{ site.url }}" class="previous">Previous</a>
					{% else %}
						<a href="{{ site.url }}/page{{paginator.previous_page}}" class="previous">Previous</a>
					{% endif %}
				{% endif %}
			</div>

			<div class="span2">
				<span class="page_number">Page: {{paginator.page}} of {{paginator.total_pages}}</span>
			</div>

			<div class="span2">
				{% if paginator.next_page %}
					<a href="{{ site.url }}/page{{paginator.next_page}}" class="next">Next</a>
				{% endif %}
			</div>
		</div>
	</div>

{% endcapture %}
{{ index_page_html | remove:'	' }}
