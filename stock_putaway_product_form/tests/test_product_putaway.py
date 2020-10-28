# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# Copyright 2020 Víctor Martínez - Tecnativa

from odoo.tests.common import TransactionCase


class TestProductPutaway(TransactionCase):
    def setUp(self):
        super().setUp()
        self.putawayRuleObj = self.env["stock.putaway.rule"]
        ProductTemplate = self.env["product.template"]
        ProductAttribute = self.env["product.attribute"]
        ProductAttributeValue = self.env["product.attribute.value"]
        TemplateAttributeLine = self.env["product.template.attribute.line"]
        ref = self.env.ref
        self.product_tmpl_chair = ref("product.product_product_11_product_template")
        self.product_product_chair = ref("product.product_product_11")
        self.category_services = ref("product.product_category_3")
        self.putaway_rule_1 = ref("stock_putaway_product_form.putaway_rule_1")
        self.putaway_rule_2 = ref("stock_putaway_product_form.putaway_rule_2")
        self.putaway_rule_3 = ref("stock_putaway_product_form.putaway_rule_3")
        self.putaway_rule_4 = ref("stock_putaway_product_form.putaway_rule_4")

        # Add a product with variants
        self.template = ProductTemplate.create(
            {"name": "Product test", "type": "consu"}
        )
        self.size_attribute = ProductAttribute.create(
            {"name": "Test size", "sequence": 1}
        )
        self.size_m = ProductAttributeValue.create(
            {"name": "Size M", "attribute_id": self.size_attribute.id, "sequence": 1}
        )
        self.size_l = ProductAttributeValue.create(
            {"name": "Size L", "attribute_id": self.size_attribute.id, "sequence": 2}
        )
        self.template_attribute_lines = TemplateAttributeLine.create(
            {
                "product_tmpl_id": self.template.id,
                "attribute_id": self.size_attribute.id,
                "value_ids": [(6, 0, [self.size_m.id, self.size_l.id])],
            }
        )
        self.template._create_variant_ids()

    def test_tmpl_has_putaways_from_category_simple(self):
        self.assertIn(
            self.putaway_rule_2, self.product_tmpl_chair.product_putaway_categ_ids,
        )
        self.product_tmpl_chair.categ_id = self.category_services
        self.assertNotIn(
            self.putaway_rule_2, self.product_tmpl_chair.product_putaway_categ_ids,
        )

    def test_tmpl_has_putaways_from_category_parent(self):
        # chair is under category: all/saleable/office
        self.assertIn(
            self.putaway_rule_3, self.product_tmpl_chair.product_putaway_categ_ids,
        )
        self.assertIn(
            self.putaway_rule_4, self.product_tmpl_chair.product_putaway_categ_ids,
        )

    def test_apply_putaway(self):
        # Create one strategy line for product template and other with a
        # specific variant
        location = self.env.ref("stock.stock_location_shop0")
        location1 = location.copy(
            {"name": "Location test 1", "location_id": location.id}
        )
        location2 = location.copy(
            {"name": "Location test 2", "location_id": location.id}
        )
        variant = self.template.product_variant_ids[1]
        rule1 = self.putawayRuleObj.create(
            {
                "sequence": 1,
                "company_id": location1.company_id.id,
                "product_tmpl_id": self.template.id,
                "location_in_id": location1.id,
                "location_out_id": location1.id,
            }
        )
        self.assertEqual(rule1.location_in_id, location1)
        rule2 = self.putawayRuleObj.create(
            {
                "sequence": 2,
                "company_id": location1.company_id.id,
                "product_id": variant.id,
                "location_in_id": location2.id,
                "location_out_id": location2.id,
            }
        )
        self.assertEqual(rule2.location_in_id, location2)
