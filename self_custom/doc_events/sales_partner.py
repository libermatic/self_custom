def autoname(doc, method):
    doc.name = doc.partner_id
    doc.route = f"partners/{doc.scrub(doc.name)}"