using System;
using System.Collections;
using System.Collections.Generic; 

namespace QuantConnect 
{
    using QuantConnect.Securities;
    using QuantConnect.Models; 
    

    
    public partial class BasicTemplateAlgorithm : QCAlgorithm, IAlgorithm 
    { 
        string SPY = "SPY";        
        Dictionary<string, SymbolData> symbols = new Dictionary<string, SymbolData>();
        //int sizeToTake = 5;
        //Initialize the data and resolution you require for your strategy:
        public override void Initialize() 
        {            
            //Initialize the start, end dates for simulation; cash and data required.
            SetStartDate(new DateTime(2010,01,01));
            SetEndDate(new DateTime(2014, 07,25)); 
            SetCash(25000); //Starting Cash in USD.
            
            symbols.Add(SPY, new SymbolData());

            symbols[SPY].TickSize = 0.01;
        

            AddSecurity(SecurityType.Equity, SPY, Resolution.Second); //Minute, Second or Tick
            Securities[SPY].Model = new CustomTransactionModel();
        }
        
       //Handle TradeBar Events: a TradeBar occurs on a time-interval (second or minute bars)
        public override void OnTradeBar(Dictionary<string, TradeBar> data) 
        {
            foreach(var symbol in symbols.Keys)
            {
                if (data.ContainsKey(symbol))
                {
                    Process(symbol, symbols[symbol], data[symbol]);
                }
            }            
        }

        //Handle Tick Events - Only when you're requesting tick data
        public override void OnTick(Dictionary<string, List<Tick>> ticks) 
        {
            foreach(var symbol in symbols.Keys)
            {
                if (ticks.ContainsKey(symbol) && ticks[symbol].Count > 0)
                {
                    //Process(symbol, symbols[symbol], ticks[symbol][ticks[symbol].Count - 1]);
                }
            }
        } 
        
        public void Process(string symbol, SymbolData d, TradeBar t)
        {
            double mid = (double)t.Close;//(t.Price);
            
            if (d.PrevPrice == 0)
            {
                d.PrevPrice = mid;
                d.LastTick = t.Time;
                return;
            }
            
            if (t.Time.Date != d.LastTick.Date)
            {
                d.PrevPrice = mid;
                d.LastTick = t.Time;
                return;
            }
            
            //if (t.AskPrice - t.BidPrice > (decimal)(3 * d.TickSize)) return;
            
            double pips = Math.Abs(d.PrevPrice - mid)/d.TickSize;
            
            if (pips > 100) return;
            double buyintensity = 0;
            double sellintensity = 0;
            
            if (d.PrevPrice > mid)
            {
                buyintensity = d.BuyIntensity.Process(0, true);
                sellintensity = d.SellIntensity.Process(pips, !d.downTick);
            }
            else if (mid > d.PrevPrice)
            {
                buyintensity = d.BuyIntensity.Process(pips, !d.upTick);
                sellintensity = d.SellIntensity.Process(0, true);
            }
            else
            {
                buyintensity = d.BuyIntensity.Process(0, true);
                sellintensity = d.SellIntensity.Process(0, true);
            }
            
            if (Portfolio[symbol].HoldStock)
            {
                if ((t.Time - d.LastTradeTime).TotalSeconds > 60)
                {
                    d.LastTradePrice = 0;                    
                    Liquidate(symbol);
                }
            }
            
            {
                if (buyintensity > 10 && buyintensity > sellintensity && !Portfolio[symbol].HoldStock)
                {
                    Order(symbol, -100);
                    d.Qty = 1;
                    d.LastTradePrice = mid;
                    d.LastTradeTime = t.Time;
                    //Debug(t.Time.ToString("yyyyMMdd HH:mm:ss.fff"));
                }
                else if (sellintensity > 10 && sellintensity > buyintensity && !Portfolio[symbol].HoldStock)
                {
                    Order(symbol, 100);
                    d.Qty = -1;
                    d.LastTradePrice = mid;
                    d.LastTradeTime = t.Time;
                    //Debug(t.Time.ToString("yyyyMMdd HH:mm:ss.fff"));
                }
            }
            
            d.upTick = mid > d.PrevPrice;
            d.downTick = d.PrevPrice > mid;
            d.PrevPrice = mid;
            d.LastTick = t.Time;
        }
    }
}