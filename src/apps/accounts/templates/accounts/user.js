{% load i18n %}

$(function () {
});

{% url "accounts:dashboard" as dashboard_url %}
{% include "core/generic.js" with dashboard=dashboard_url %}
