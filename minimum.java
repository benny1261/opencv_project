	public static int Minimum(int [] data ) {
		if (data.length < 2)
			return 0;
		// J. M. S. Prewitt and M. L. Mendelsohn, "The analysis of cell images," in
		// Annals of the New York Academy of Sciences, vol. 128, pp. 1035-1053, 1966.
		// ported to ImageJ plugin by G.Landini from Antti Niemisto's Matlab code (GPL)
		// Original Matlab code Copyright (C) 2004 Antti Niemisto
		// See http://www.cs.tut.fi/~ant/histthresh/ for an excellent slide presentation
		// and the original Matlab code.
		//
		// Assumes a bimodal histogram. The histogram needs is smoothed (using a
		// running average of size 3, iteratively) until there are only two local maxima.
		// Threshold t is such that yt-1 > yt ≤ yt+1.
		// Images with histograms having extremely unequal peaks or a broad and
		// ﬂat valley are unsuitable for this method.
		int iter =0;
		int threshold = -1;
		int max = -1;
		double [] iHisto = new double [data.length];

		for (int i=0; i<data.length; i++){
			iHisto[i]=(double) data[i];
			if (data[i]>0) max =i;
		}
		double[] tHisto = new double[iHisto.length] ; // Instead of double[] tHisto = iHisto ;
		while (!bimodalTest(iHisto) ) {
			 //smooth with a 3 point running mean filter
			for (int i=1; i<data.length - 1; i++)
				tHisto[i]= (iHisto[i-1] + iHisto[i] +iHisto[i+1])/3;
			tHisto[0] = (iHisto[0]+iHisto[1])/3; //0 outside
			tHisto[data.length - 1] = (iHisto[data.length - 2]+iHisto[data.length - 1])/3; //0 outside
			System.arraycopy(tHisto, 0, iHisto, 0, iHisto.length) ; //Instead of iHisto = tHisto ;
			iter++;
			if (iter>10000) {
				threshold = -1;
				IJ.log("Minimum Threshold not found after 10000 iterations.");
				return threshold;
			}
		}
		// The threshold is the minimum between the two peaks. modified for 16 bits
		
		for (int i=1; i<max; i++) {
			//IJ.log(" "+i+"  "+iHisto[i]);
			if (iHisto[i-1] > iHisto[i] && iHisto[i+1] >= iHisto[i]){
				threshold = i;
				break;
			}
		}
		return threshold;
	}