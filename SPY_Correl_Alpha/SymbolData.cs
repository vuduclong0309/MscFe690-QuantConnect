using System;
using System.Collections;
using System.Collections.Generic;
using QuantConnect.Securities;
using QuantConnect.Models;

namespace QuantConnect {

    public class SymbolData
    {
        private Hawkes i = new Hawkes(1, 1.2, 1.8);
        private Hawkes b = new Hawkes(1, 1.2, 1.8);
        private Hawkes s = new Hawkes(1, 1.2, 1.8);
        
        public double LastTradePrice { get; set; }
        public DateTime LastTradeTime { get; set; }
        public Hawkes Intensity { get { return i; }  }
        public Hawkes BuyIntensity { get { return b; } }
        public Hawkes SellIntensity { get { return s; } }
        public double TickSize { get; set; }
        public double PrevPrice { get; set; }
        public bool upTick { get; set; }
        public bool downTick { get; set; }
        public DateTime LastTick { get; set; }  
        public int Qty { get; set; }
    }
}
