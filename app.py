from flask import Flask, render_template, jsonify
import random
import os

app = Flask(__name__)

# カードタイプと対応する抽選確率
card_probabilities = {
    'N': 0.33,
    'N+': 0.25,
    'R': 0.20,
    'R+': 0.15,
    'SR': 0.05,
    'SR+': 0.02
}

eleven_gacha_probabilities = {
    'R': 0.57,
    'R+': 0.30,
    'SR': 0.10,
    'SR+': 0.03
}

gacha_price = 100
eleven_gacha_price = 1000

# 画像フォルダのパス（カードタイプに対応するフォルダを設定）
image_folders = {
    'N': 'static/images/N/',
    'N+': 'static/images/N+/',
    'R': 'static/images/R/',
    'R+': 'static/images/R+/',
    'SR': 'static/images/SR/',
    'SR+': 'static/images/SR+/'
}

class GachaSimulator:
    def __init__(self):
        self.reset()

    def draw_single(self):
        self.total_cost += gacha_price
        self.total_draws += 1
        card = self._get_card(card_probabilities)
        self.card_counts[card] += 1
        self.cards.append((card, self._get_image(card)))
        if card == 'SR+':
            self.total_sr_plus_draws += 1

    def draw_eleven(self):
        self.total_cost += eleven_gacha_price
        self.total_draws += 11
        # 十連ガチャ、毎回10枚を引き、最後の1枚はSR確定
        cards = [(self._get_card(eleven_gacha_probabilities), self._get_image(self._get_card(eleven_gacha_probabilities))) for _ in range(10)]
        cards.append(('SR', self._get_image('SR')))
        for card, _ in cards:
            self.card_counts[card] += 1
        self.cards.extend(cards)
        if 'SR+' in [card[0] for card in cards]:
            self.total_sr_plus_draws += 1

    def _get_card(self, probabilities):
        rand = random.random()
        cumulative_prob = 0.0
        # 確率に基づいてカードを抽選
        for card, prob in probabilities.items():
            cumulative_prob += prob
            if rand <= cumulative_prob:
                return card
        return 'N'  # デフォルトで'N'カードを返す

    def _get_image(self, card_type):
        # カードタイプに対応する画像のパスを取得
        folder = image_folders[card_type]
        image_files = os.listdir(folder)
        return os.path.join(folder, random.choice(image_files))

    def reset(self):
        self.total_cost = 0
        self.total_draws = 0
        self.card_counts = {'N': 0, 'N+': 0, 'R': 0, 'R+': 0, 'SR': 0, 'SR+': 0}
        self.cards = []
        self.total_sr_plus_draws = 0
        self.sr_plus_cost_cache = None  # "全種類SR+カードのコスト"のキャッシュ

    def calculate_sr_plus_cost(self):
        if self.sr_plus_cost_cache is not None:
            return self.sr_plus_cost_cache

        target_sr_plus_cards = 6
        cost = 0
        sr_plus_cards_found = set()

        while len(sr_plus_cards_found) < target_sr_plus_cards:
            self.draw_single()
            cost += gacha_price
            if self.cards[-1][0] == 'SR+':
                sr_plus_cards_found.add(self.cards[-1][0])

        self.sr_plus_cost_cache = (cost, self.total_draws, self.card_counts)
        return self.sr_plus_cost_cache


simulator = GachaSimulator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/draw_single')
def draw_single():
    simulator.draw_single()
    return jsonify({
        'totalCost': simulator.total_cost,
        'totalDraws': simulator.total_draws,
        'cardCounts': simulator.card_counts,
        'cards': [{'image': card[1]} for card in simulator.cards]
    })

@app.route('/draw_eleven')
def draw_eleven():
    simulator.draw_eleven()
    return jsonify({
        'totalCost': simulator.total_cost,
        'totalDraws': simulator.total_draws,
        'cardCounts': simulator.card_counts,
        'cards': [{'image': card[1]} for card in simulator.cards]
    })

@app.route('/reset')
def reset():
    simulator.reset()
    return jsonify({
        'totalCost': simulator.total_cost,
        'totalDraws': simulator.total_draws,
        'cardCounts': simulator.card_counts,
        'cards': []
    })

@app.route('/calculate_sr_plus_cost')
def calculate_sr_plus_cost():
    cost, draws, counts = simulator.calculate_sr_plus_cost()
    return jsonify({
        'cost': cost,
        'draws': draws,
        'cardCounts': counts
    })

if __name__ == '__main__':
    app.run(debug=True)