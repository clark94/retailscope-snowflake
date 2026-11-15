import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from local_data import load_local

class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.sales,cls.stocks,cls.goals,cls.rejects,cls.duplicates=load_local()
    def test_reconciliation(self):
        self.assertEqual((len(self.sales),len(self.rejects),self.duplicates),(6000,6,10))
        self.assertEqual(self.sales.ligne_id.nunique(),6000)
        self.assertEqual(self.sales.commande_id.nunique(),3000)
    def test_amounts_independent_decimal(self):
        from decimal import Decimal,ROUND_HALF_UP
        total=Decimal('0')
        for r in self.sales.itertuples():
            total+=(Decimal(str(r.quantite))*Decimal(str(r.prix_unitaire))*(1-Decimal(str(r.remise)))).quantize(Decimal('.01'),rounding=ROUND_HALF_UP)
        self.assertAlmostEqual(float(total),self.sales.ca_net.sum(),places=2)
    def test_dimension_and_stock_grain(self):
        self.assertEqual(len(self.stocks),180)
        self.assertFalse(self.stocks.duplicated(['date_stock','magasin_id','produit_id']).any())
        self.assertEqual(len(self.goals),36)
        self.assertEqual(len(set(self.rejects.motif)),6)
    def test_repeatable_and_order_consistency(self):
        import pandas as pd
        again,*_=load_local()
        pd.testing.assert_frame_equal(self.sales,again)
        self.assertEqual(self.sales.groupby('commande_id').date_vente.nunique().max(),1)
        self.assertEqual(self.sales.groupby('commande_id').magasin_id.nunique().max(),1)
if __name__=='__main__':unittest.main()
