from plugins.interfaces.tui.screens import TemplateFormScreen


def test_template_form_creation():
    form = TemplateFormScreen()
    assert form is not None


def test_template_form_with_template():
    template = {"name": "uptime", "command": "uptime", "description": "Show uptime"}
    form = TemplateFormScreen(template=template)
    assert form.template == template
