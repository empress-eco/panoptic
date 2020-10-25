# -*- coding: utf-8 -*-
# Copyright (c) 2020, Internet Freedom Foundation and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.website.website_generator import WebsiteGenerator

class State(WebsiteGenerator):

	published = 1
	website = frappe._dict(
		page_title_field="state_name",
		no_cache=1,
		sitemap=1
	)

	def autoname(self):
		self.name = self.state_name

	def get_context(self, context):
		context.frts = self.get_all_frts(filters={ "state": self.name })

		context.total_frt = frappe.db.count("FRT", {"state": self.name}) or 0
		context.total_frt_in_use = frappe.db.count("FRT", {"state": self.name, "status": "In Utilization"}) or 0
		context.total_cost = sum(frappe.db.get_all("FRT", fields=["amount_spent"], filters={ "state": self.name }, pluck="amount_spent"))

		context.state_wise_frt = get_state_wise_frt()
		context.state_routes = get_state_route_map()

	def get_all_frts(self, filters={}, fields=None):
		if not fields:
			fields = ["name", "authority", "district_name", "technology_provider", "route"]

		filters.update({
			"published": 1
		})

		return frappe.get_all("FRT", fields=fields, filters=filters, limit=30)


def get_state_route_map():
	states = frappe.get_all("State", fields={"state_id", "route"})
	return {d.state_id:d.route for d in states}

def get_state_wise_frt(cache=True):
	data = frappe.db.sql("""
		SELECT
			`st`.`state_id`,
			count(`frt`.`name`) as count
		FROM
			`tabFRT` as `frt`,
			`tabState` as `st`
		WHERE
			`frt`.`state`=`st`.`name`
		GROUP BY
			`frt`.`state`
	""", as_dict=1)

	return {d.state_id:d.count for d in data}