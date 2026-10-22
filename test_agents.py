import unittest
from agents import ForecastingAgent, AggregationAgent, PricingEngine, NegotiationAgent

class AgentTests(unittest.TestCase):
    def setUp(self):
        self.weavers = [
            {'id':1,'name':'A','product':'Silk Saree','capacity':5,'committed':1,'unit_cost':100,'quality':'Standard','status':'Active'},
            {'id':2,'name':'B','product':'Silk Saree','capacity':8,'committed':0,'unit_cost':120,'quality':'Standard','status':'Active'},
        ]
    def test_forecast_recent_mean(self):
        self.assertEqual(ForecastingAgent().forecast([10,20,30])['forecast'],20)
    def test_allocation_respects_capacity(self):
        result=AggregationAgent().allocate(self.weavers,'Silk Saree',10)
        self.assertTrue(result['feasible'])
        self.assertEqual(result['allocated'],10)
        self.assertLessEqual(sum(x['quantity'] for x in result['allocations']),sum(x['capacity']-x['committed'] for x in self.weavers))
    def test_shortage_reported(self):
        result=AggregationAgent().allocate(self.weavers,'Silk Saree',99)
        self.assertFalse(result['feasible'])
        self.assertGreater(result['shortage'],0)
    def test_below_floor_counteroffer(self):
        pricing={'units':2,'break_even_unit':100,'target_unit':110,'total_cost':200}
        result=NegotiationAgent().evaluate(90,pricing,30,True,45)
        self.assertTrue(result['below_floor'])
        self.assertEqual(result['action'],'COUNTEROFFER')
    def test_long_payment_escalates(self):
        pricing={'units':1,'break_even_unit':100,'target_unit':110,'total_cost':100}
        result=NegotiationAgent().evaluate(120,pricing,90,True,45)
        self.assertEqual(result['action'],'HUMAN_REVIEW')

if __name__=='__main__': unittest.main()
