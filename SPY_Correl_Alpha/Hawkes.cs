// QuantConnect Simulator C# File, Created on 3-6-2014 by Satyapravin Bezwada
using System;
using System.Collections;
using System.Collections.Generic;

namespace QuantConnect {
    public class Hawkes
    {
        double mu_ = 0, alpha_ = 0, beta_ = 0, bfactor_ = 0;

        public Hawkes(double mu, double alpha, double beta)
        {
            mu_ = mu;
            alpha_ = alpha;
            beta_ = beta;
        }

        public double Process( double count, bool decay)
        {
            double exp = Math.Exp(-beta_);
            
            if (decay) bfactor_ *= exp;
            bfactor_ += exp * count;
            return mu_ + alpha_ * bfactor_;
        }
    }
}