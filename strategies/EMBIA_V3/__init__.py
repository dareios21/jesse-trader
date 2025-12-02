from jesse.strategies import Strategy
import jesse.indicators as ta
from jesse import utils

# Embi/b48 @ Discord 
#just cookin up some spaghetti strategies

class EMBIA_V3(Strategy):
    
    @property
        # Filter dis badboi by volume weighted MA on big timeframe
    def vwma_filter(self):
        return ta.vwma(self.higher_timeframe_candles, period=51)

    @property
    def srsi_inverted(self):
        # Calculate the big autistic rsi
        return ta.srsi(self.higher_timeframe_candles).k

    @property
    def srsi(self):
        # Calculate the small autistic rsi
        return ta.srsi(self.candles).k
    
    @property
         # Sprinkle in three small vwma's
    def vwma_fast(self):
        return ta.vwma(self.candles, period=5)
        # Bam
    @property
    def vwma_medium(self):
        return ta.vwma(self.candles, period=8)
        # Bam Bam
    @property
    def vwma_slow(self):
        return ta.vwma(self.candles, period=13)

    @property
        #Obligatory Average D Index
    def adx(self):
        return ta.adx(self.candles)

    @property
        # Almost forgot this, lmao
    def higher_timeframe_candles(self):
        return self.get_candles(self.exchange, self.symbol, '1h')

        # Some of these fast bois on the big timeframe too
    @property
    def higher_vwma_fast(self):
        return ta.vwma(self.higher_timeframe_candles, period=5)

        # Wham
    @property
    def higher_vwma_medium(self):
        return ta.vwma(self.higher_timeframe_candles, period=8)

        #Wham Bam Slam
    @property
    def higher_vwma_slow(self):
        return ta.vwma(self.higher_timeframe_candles, period=13)


        # OK, tongue in mouth now
    def should_long(self) -> bool:
        return (self.vwma_fast > self.vwma_medium > self.vwma_slow and
                self.adx > 28 and self.price > self.vwma_filter and self.srsi_inverted < 90 and self.srsi < 20 and
                self.higher_vwma_fast > self.higher_vwma_medium > self.higher_vwma_slow)

    def go_long(self):
        # Low drawdown, so ill slap a 5x qty on this sucker
        entry = self.price
        stop = entry - ta.atr(self.candles) * 2.85  # Set stop loss based on ATR
        qty = utils.risk_to_qty(self.available_margin, 6, entry, stop, fee_rate=self.fee_rate)  # Calculate position size
        self.buy = qty*5, entry  # Place buy market order

        # More keeping tounge in mouth
    def should_short(self) -> bool:
        return (self.vwma_fast < self.vwma_medium < self.vwma_slow and
                self.adx > 28 and self.price < self.vwma_filter and self.srsi_inverted > 10 and self.srsi > 80 and
                self.higher_vwma_fast < self.higher_vwma_medium < self.higher_vwma_slow)

    def go_short(self):
        # Size up this suckaaaa aswell
        entry = self.price
        stop = entry + ta.atr(self.candles) * 2.85  # Set stop loss based on ATR
        qty = utils.risk_to_qty(self.available_margin, 6, entry, stop, fee_rate=self.fee_rate)  # Calculate position size
        self.sell = qty*5, entry  # Place sell market order

        #This shits probably useless at this point, but i got faith in it working some kind of magic
    def on_open_position(self, order):
        atr_value = ta.atr(self.candles)
        if self.is_long:
            stop_loss = self.price - (atr_value * 2.85)
            take_profit = self.price + (atr_value * 3.4)
        else:
            stop_loss = self.price + (atr_value * 2.85)
            take_profit = self.price - (atr_value * 3.4)

        self.stop_loss = self.position.qty, stop_loss
        self.take_profit = self.position.qty, take_profit

    def should_cancel_entry(self) -> bool:
        return False