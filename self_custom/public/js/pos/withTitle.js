export default function withTitle(PointOfSale) {
  return class PointOfSaleWithTitle extends PointOfSale {
    make() {
      return super.make().then(() => {
        this.page.set_title_sub(this.frm.doc.pos_profile);
      });
    }
    on_change_pos_profile() {
      return super.on_change_pos_profile().then(() => {
        this.page.set_title_sub(this.frm.doc.pos_profile);
      });
    }
  };
}
