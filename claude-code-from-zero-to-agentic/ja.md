# Claude Codeを本気で使いこなす：Skills、Hooks、サンドボックス、サブエージェント

ChatGPT には慣れていて、Claude Code も同じ感覚で使えるようにしたい人向けの実践ガイドです。そこからさらに三、四歩先まで進みます。

この記事は意図的に長くしています。最初は上から下まで一度通して読むのがおすすめです。ブックマークしておいて、実際に必要になったら [7. Skills: 探す、入れる、使う](#7-skills-discovering-installing-using) 以降に戻ってきてください。

> 対象は Claude Code v2.1.145、2026年5月時点です。バージョンの進みが速いので、最近入った機能については、挙動が違うと感じたときに [release notes](https://github.com/anthropics/claude-code/releases) と照らし合わせられるようにしておきます。

> もう 1 つ大事なこととして、[Claude アカウントがどう課金されているか](https://claude.ai/settings/usage)は先に確認してください。Pro / Max では主に利用枠や週次上限を意識しますが、Enterprise では、独自の spending cap があり、API 料金ベースで課金される場合があります。詳しくは [12章](#12-the-not-so-cool-basics-that-actually-matter) で扱いますが、Opus のような高いモデルで何時間も作業する前に知っておくべき話です。

---

## 目次

1. [ChatGPT から Claude Code へ](#1-from-chatgpt-to-claude-code)
2. [CLAUDE.md はリポジトリでいちばん大事なファイル](#2-claudemd-is-the-most-important-file-in-your-repo)
3. [Claude に実作業を頼む](#3-asking-claude-to-do-real-work)
4. [内側のループ: 権限とモード](#4-the-inner-loop-permissions-and-modes)
5. [セッションを再開する](#5-resuming-sessions)
6. [コンテキスト: 溜める、圧縮する、消す](#6-context-piling-up-compacting-clearing)
7. [Skills: 探す、入れる、使う](#7-skills-discovering-installing-using)
8. [自分の Skills を作る](#8-creating-your-own-skills)
9. [ガードレール: hooks](#9-guardrails-hooks)
10. [Sandboxes](#10-sandboxes)
11. [本当にエージェント的に使う: 高度な機能](#11-truly-agentic-the-advanced-features)
12. [地味だけど本当に大事な基礎](#12-the-not-so-cool-basics-that-actually-matter)
13. [よくある失敗パターン](#13-common-failure-modes)
14. [次に見るもの](#14-where-to-go-next)
15. [Bonus](#15-bonus)

---



## 1. ChatGPT から Claude Code へ

ChatGPT を使ったことがあれば、Claude Code の仕組みの 80% はすでに理解できています。残りの 20% が、いい意味で危険な部分です。

Claude Code は単なるチャットではありません。コードの隣に住む CLI エージェントです。プロンプトを渡すと、返事をするだけでなく、許可を取ったうえで次のことができます。

- プロジェクト内のファイルを読む
- シェルコマンドを実行する
- ディスク上のコードを編集する

.. すべて許可ベースです。手を動かせるシニアのペアプログラマーだと思うと近いです。

### どこで動かせるか

主な選択肢は 4 つあります。自分がよく使う順に並べます。

1. **Terminal（推奨）**。任意のディレクトリで `claude` と打つだけです。これが標準体験です。機能はまずここに入り、キーボードだけのワークフローも 1 日ほどで違和感がなくなります。この記事の内容は、基本的にここにいる前提で書いています。
2. **VS Code / Cursor / JetBrains plugin（次点）**。同じエンジンですが、diff のプレビューが見やすく、エディタにいながら作業できます。IDE 中心で作業しているなら入れる価値があります。ただし、Terminal 版ほど成熟していない点は覚えておいたほうがいいです。
3. **Desktop app（Mac / Windows）**。UI は洗練されていて、コーディング以外のタスクや、ちゃんとしたテキストエディタで会話したいときに向いています。一部の高度なフラグや slash command は反映が遅れます。Desktop app にはいくつかバグがあり、Terminal 版ほど安定していないという話も聞きますが、自分ではまだ使い込んでいません。
4. **Web at [claude.ai/code](https://claude.ai/code)**。手元のマシンから離れているときの単発質問、"ultraplan" モード、Anthropic 側のインフラで動く [scheduled routines](#11-truly-agentic-the-advanced-features) を起動する用途に向いています。日常的に作業する場所としては、だいたいここではありません。

### インストール

インストール手順はよく変わるので、ここでは再掲しません。[official quickstart](https://docs.claude.com/en/docs/claude-code/quickstart) を参照してください。

Windows を使っている場合は、Windows Subsystem for Linux (WSL) を使い、WSL のターミナル内に Claude Code を入れることを強くおすすめします。そうすると Claude Code を開くたびに最新バージョンを使いやすくなります。Windows PowerShell や Command Prompt で普通に使うのも問題ありませんが、WinGet で入れた場合は自動更新されないため、ときどき手動更新が必要になるかもしれません。最終的には好みです。

macOS の場合は、curl で Claude Code を入れるのがおすすめです。これは Anthropic も推奨しているネイティブな方法です。個人的な経験として、Homebrew 経由はおすすめしていません。

`claude --version` が動くようになったら戻ってきてください。

### 最初の例を 2 つ

Terminal で、よく知っているプロジェクトに `cd` します。どんなプロジェクトでも大丈夫です。そこで次のコマンドを実行します。

```bash
claude
```

welcome-banner

これが起動時の welcome banner です。

プロンプトが出ます。次を試します。

```claude
what does this repo do?
```

what-does-this-repo-do

Claude はリポジトリの README、トップレベルのファイル、場合によっては `package.json` や `pyproject.toml` などを必要なだけ読んで答えます。やったことは、プロジェクトディレクトリに `cd` して、`claude` を起動し、シンプルな質問を 1 つしただけです。ここが ChatGPT との違いです。

まだプロジェクトに README.md がない場合は、次のコマンドを貼って作成します。すでに README.md がある場合は、この手順は飛ばしてください。

```bash
echo "# README.md\n\nLearning LoRA and finetuning by doing my own experiment where I compare three versions of the same \`Qwen3-8B\` math run:\n\n1. the untouched baseline\n2. LoRA on the attention projections\n3. LoRA on both attention and feed-forward projections.\n\nThis project came to mind when I was reading the \"LoRA Without Regret\" blog post by Thinking Machines; so many research ideas to explore! Well, I only knew LoRA conceptually before this, and I have never done any serious finetuning before except for a hackathon, so I think this challenge I have set for myself is pretty nice.\n" > README.md
```

次にこれを試します。

```claude
@README.md what's missing from this README that a new contributor would want?
```

whats-missing-from-this-readme

`@` は fuzzy file picker を起動します。選んだファイルはコンテキストに読み込まれます。これが最初の少し本格的な能力です。**Claude Code は指定したものを見られます。**

### メンタルモデル

> Claude Code は、ファイルシステムを見られて、許可を取ったうえで何かを実行できる ChatGPT です。

この一文でほぼ 90% は説明できます。チャットにコードをコピペしたくなるたびに思い出してください。コピペする必要はありません。ファイルを指し示せばいいだけです。

---



## 2. CLAUDE.md はリポジトリでいちばん大事なファイル

この記事で 1 つだけ覚えるなら、**リポジトリに `CLAUDE.md` を置く**ことです。いちばんレバレッジの高い変更と言ってもいいくらいです。

`CLAUDE.md` は Markdown ファイルで、Claude Code はそのディレクトリでセッションを始めるたびに自動で読み込みます。コードからは推測できないこと、たとえば規約、コマンド、注意点、「pip ではなく uv を使う」などを Claude に伝えるための場所です。毎回同じ説明を繰り返さなくて済みます。

### 置き場所

Claude Code は `CLAUDE.md` を次の 3 か所で探します。この順番です。


| Path                        | Scope                                             |
| --------------------------- | ------------------------------------------------- |
| `~/.claude/CLAUDE.md`       | User-level。個人設定。すべてのプロジェクトに適用されます。                |
| `<repo>/CLAUDE.md`          | Project-level。git に入れ、チームで共有します。                  |
| `<repo>/<subdir>/CLAUDE.md` | Subdirectory-level。その subtree で作業しているときだけ読み込まれます。 |


加えて `CLAUDE.local.md` もあります。これは `<repo>/CLAUDE.md` と同じですが、慣例的に `.gitignore` します。コミットしたくない個人メモに使います。

個人的には、`CLAUDE.md` はプロジェクトルートに置き、user level には置かないほうが好みです。たとえばこうです。

```bash
project-name/
├── src/
│   ├── cute/
│   │   ├── blackwell_helpers.py
│   │   ├── flash_fwd.py
│   │   └── paged_kv.py
│   ├── layers/
│   ├── models/
├── examples/
│   ├── inference/
├── docs/
│   ├── architecture.md
│   └── testing-guidelines.md
├── CLAUDE.md      # <-- here
├── .gitignore
├── .env
├── Makefile
├── README.md
└── LICENSE
```

### `/init`

始める最短ルートは、リポジトリで新しい `claude` セッションを開き、次を打つことです。

```claude
/init
```

claudeinit

Claude がリポジトリを調べて `CLAUDE.md` を提案します。確認して、削って、受け入れます。そのまま受け入れるのは避けたほうがいいです。余計なことまで入りすぎる場合があります。

### 良い CLAUDE.md に入れるもの

Anthropic の [ベストプラクティスのdoc](https://code.claude.com/docs/ja/best-practices) には良い ✅/❌ の表があります。要点はこうです。

✅ 入れるもの:

- Claude が推測できない Bash コマンド（`npm run lint`, `make watch`, `pnpm test:integration`）。
- linter 設定にはないコードスタイル規則（`prefer named exports`, `match the existing pattern in src/api/`）。
- ワークフロー上の約束（`always update the changelog`, `branch from main`, `we squash on merge`）。
- リポジトリ固有の癖（`the .env in services/auth is different from the others`, `don't touch generated/`）。

❌ 入れないもの:

- Claude がデフォルトで十分できること。バグ修正を頼んだら普通にテストを書くなら、「バグ修正ではテストを書け」を CLAUDE.md に足す必要はありません。
- 長い理由説明。なぜそうするかは design doc に置きます。
- ファイルツリーの再掲。Claude は `ls` できます。
- 実際の判断に効かない曖昧な包括ルール（「気をつける」「良い判断をする」）。

Claude Code の作者である Boris Cherny は、[Claude Code patterns post](https://howborisusesclaudecode.com/) でかなりはっきり言っています。Claude がその instruction なしでもできているなら、その instruction は消す。`CLAUDE.md` は雰囲気を足す場所ではなく、摩擦を減らす場所です。

### 他のファイルを import する

`@` 構文を使うと、CLAUDE.md に他のファイルを取り込めます。

```markdown
# Conventions for this repo

We use uv, not pip. We use ruff, not black.

@./docs/architecture.md
@./docs/testing-guidelines.md
```

Imports はセッション開始時に解決されます。`architecture.md` が長ければ、最初のターンから context window に入ると思ってください。

### Auto memory

Claude Code には、セッションをまたいで Claude 自身が memory を積み上げる機能があります。役割、好み、プロジェクト状態などの小さなメモです。直接管理するものではなく、`~/.claude/projects/<project-hash>/memory/` の下に置かれます。特に何かする必要はありません。ただ、`CLAUDE.md` が唯一の永続化手段ではなくなっていることを知っておくのは役に立ちます。それでも、`CLAUDE.md` は自分で管理でき、新しいセッションが最初に信頼するものです。

---



## 3. Claude に実作業を頼む

CLAUDE.md はできました。では、実際に Claude に何かを「やって」もらうにはどうすればいいのでしょうか。

### 4 つの入力プリミティブ


| You type                        | What happens                              |
| ------------------------------- | ----------------------------------------- |
| `@filename`                     | Fuzzy file picker。選んだファイルが context に入ります。 |
| `!command`                      | シェルコマンドを実行し、その出力を prompt に入れます。           |
| Drag/drop image                 | 画像が context に入ります。paste でも動きます。           |
| `cat err.log | claude -p "..."` | stdin を one-shot prompt に流し込みます。          |


いちばんよく使うのは最初の `@` です。`@` に慣れると、コピペはほぼしなくなります。

file-picker

### ライブデモ

プロジェクトディレクトリに下書きのブログ記事を作ってみます。次を打ちます。

```claude
make a draft at drafts/hello.md with a short intro to Claude Code,
suitable for someone who's used chatgpt
```

drafts-hello

Claude はファイルを提案し、内容を見せ、許可を求めます。承認すると書き込みます。次に、Claude Code にこれを貼ります。

```claude
@drafts/hello.md add a 3-section TOC at the top: intro, examples,
gotchas, and stub each section with a one-line placeholder.
```

diff-of-new-toc

Claude はファイルを読み、編集内容を計算し、diff を表示し、許可を求めました。ChatGPT では起きなかった 3 つのことが起きています。実ファイルを読み、ディスクに書き、承認または却下できる diff を出しました。

### 効く prompting

ChatGPT と同じように prompt しても、Claude はそれなりに動きます。少しだけ頼み方を変えると、かなりよく動きます。[best-practices doc](https://docs.claude.com/en/docs/claude-code/best-practices) の 4 つのコツを短くまとめるとこうです。

1. **タスクの範囲を切る。** 「バグを直して」ではなく、「`id` が数値でないときに `/users/:id` が 500 を返すバグを直す。まず再現し、その後修正し、テストを追加する」。
2. **情報源を指す。** 関係あると分かっているファイルは `@` で指定します。Claude に grep させる前に渡します。
3. **既存パターンを参照する。** 「この新機能を追加するときは `src/api/v2/handlers/` のパターンに合わせる」。具体例は one-shot / few-shot examples として効き、抽象ルールより強いです。
4. **仮説ではなく症状を説明する。** 「cache layer が壊れている」と言うと、そこだけ見に行きます。バグが upstream にあってもです。観測したことを伝え、診断は任せます。

裏返すと、ChatGPT 的に「X をする関数を書いて」と頼んでいるだけでは、価値の大半を使えていません。Claude Code の強みは context を読めることです。必要な材料をちゃんと渡しましょう。

---



## 4. 内側のループ: 権限とモード

最初に多くの人がぶつかる壁は、ほぼすべての action で許可を求められることです。10 分もすると laptop を投げたくなります。そこから抜ける階段があります。覚えておく価値があります。

### 権限の階段

信頼度が低い順に並べます。

#### 1. Default（書き込みと実行の前に毎回聞く）

初日に見る状態です。編集、シェルコマンド、すべてで permission prompt が出ます。

permission-to-rm

そのセッションをまだ信頼していないときや、タスクが sensitive なときに使います。

#### 2. Plan mode（Shift+Tab を 2 回、または `/plan`）

このモードでは Claude Code は読むことと探索だけできます。編集、書き込み、実行はできません。その代わり、レビューできる計画をファイルに出します。多くの場合 `~/.claude/plans/<slug>.md` です。

plan-mode

慣れていないコードベースに入るときや、そこそこ大きい変更を始める前に使います。本物のエンジニアがやるのと同じです。まず探索し、計画し、それから実行する。ただし、もう少し構造化されています。

plan mode はかなり好きです。単純ではなく、ある程度の reasoning や手順の整理が必要なタスクでは、いつも plan mode を使います。

#### 3. acceptEdits（Shift+Tab で切り替え）

ファイル編集と安全な filesystem 操作（安全な path への `mkdir`, `touch`, `mv`, `cp`）を自動承認します。任意のシェルコマンドは自動承認しません。

acceptedits

> acceptEdits mode でも、protected paths（`.git`, `.claude`, dotfiles, home directory 自体）は守られます。acceptEdits は「diff を信頼する」であって、「全部を信頼する」ではありません。

注意を払いながら diff を確認しているが、40 回 `Approve` を押したくないときに使います。

#### 4. Auto mode (`claude --permission-mode auto`)

比較的新しく、知っておく価値があります。小さな classifier model が Bash と MCP calls を gate しているようです。scope escalation、未知の infrastructure、敵対的に見える content をブロックし、routine に見えるものは通します。classifier が 3 回連続でブロックすると、permission prompt に戻ります。Sonnet 4.6 以降と Max/Team/Enterprise plan が必要です。

2026年5月21日時点では、このモードは Pro plan では使えません。ただし、[Anthropic は 3月24日の blog](https://claude.com/blog/auto-mode) で Enterprise plan と API users には "in the coming days" に来ると述べていました。いつ使えるようになるかは分かりません。ただ、近いうちに使えるようになることを期待して、ここで触れておきます。

#### 5. bypassPermissions / `--dangerously-skip-permissions`

チェックなし。全速力。何も聞かれません。

> **まだ使わないでください。** [9章](#9-guardrails-hooks) で hooks に戻ってきます。それが入ってからなら、`--dangerously-skip-permissions` は意図的な選択になります。

### `/permissions` allowlists

特定のコマンドを always-allowed として固定できます。セッション内でこうします。

```claude
/permissions allow Bash(npm run lint)
/permissions allow Bash(pytest *)
```

これで、そのコマンドは default mode でも permission prompt なしに実行されます。prompt を意味のある場所に残すための方法です。破壊的なコマンドは gate したまま、安全なものだけ nagging を止めます。

`/permissions list` で現在 allow されているものを表示します。`/permissions deny <rule>` で削除します。

### どのモデルを使うべきか

普段はほとんどのタスクで最新の Opus を使い、計画づくりには Sonnet を使っていました。タスクがよく整理されていて手順に自信があるなら、最初から最後まで Sonnet でも大丈夫です。Opus のほうが明らかに強いですが、Sonnet も悪くありません。`/model` に行けば、使いたいモデルに切り替えられます。

ただし、モデル選びを単なる品質の話として扱う前に、課金のされ方は確認したほうがいいです。通常の Pro / Max subscription では、主に利用枠や週次上限を気にします。一方、usage-based Enterprise や API key での利用では、使った分が API 料金で課金されるため、モデル選びがそのまま費用に効きます。この場合、Opus を一日中つけっぱなしにすると、spend cap を想像以上に速く使い切ることがあります。Haiku は本格的なコーディングにはあまりおすすめしません。実用上は、考える部分だけ Opus で進め、作業がはっきりしたら Sonnet に戻す、くらいがだいたい良いです。

さらに、2026年5月21日時点では、model effort を low から max まで設定できます。effort が高いほど、モデルは詳しい reasoning と analysis に時間を使います。`max` effort は効果のわりに token を使いすぎると感じることが多く、`high` や `xhigh` で十分なことが多いです。

---



## 5. セッションを再開する

昨日の debugging session、数日にまたがる feature、途中の refactor。もう一度説明する必要はありません。Claude Code はセッションを自動で残してくれます。

### resume flags

```bash
claude --continue           # or `claude -c` --- この dir の最新 session を再開
claude --resume             # 全 session から interactive picker
claude --resume my-oauth    # 名前付き session に飛ぶ
```

claude-resume

### セッションに名前を付ける

セッション内でこうします。

```claude
/rename my-oauth-refactor
```

後で探すなら、"ff347a49-e961-444f-9dae-28553602ead5" より名前のほうがずっと楽です。戻ってくる可能性があるものには名前を付けます。

### Checkpoints と `/rewind`

Claude Code は各変更の前に checkpoint を自動で作ります。巻き戻すには:

- `Esc Esc`: rewind menu を開く。
- `/rewind`: slash command で同じ menu を開く。

rewind1



rewind2

巻き戻し方は選べます。

- **Conversation only**: file edits は残し、chat history だけ戻す。「今の聞き方をやり直したい」に便利。
- **Code only**: 会話は続け、disk changes だけ戻す。
- **Both**: その turn への完全な time-machine。
- **"Summarize from here"** または **"summarize up to here"**: 部分的な compaction（詳しくは [6章](#6-context-piling-up-compacting-clearing)）。

> Checkpoints が追跡するのは Claude の編集であり、外部プロセスではありません。長時間の build がファイルを書いた場合、それは戻りません。`/rewind` を git の代わりとして扱わないでください。Git は本当に大事です。変更追跡には必ず使うことをおすすめします。

### Teleporting

Web app や desktop app で始めたセッションを terminal で終わらせたい場合、`claude --teleport` で移せます。スマホで始めて laptop で終えるような使い方に便利です。

---



## 6. コンテキスト: 溜める、圧縮する、消す

Claude が読んだファイル、実行したコマンド、見た出力はすべて context window に入ります。長いセッションは遅く、高く、だんだん変になります。モデルが 2 時間前に言ったことを忘れ始めます。

これを管理する道具は 4 つあります。正しいものを使います。

### `/compact` : その場で要約

```claude
/compact
```

Claude は現在のセッションをその場で要約し、要点を残して細部を落とします。会話はその summary から続きます。

compact

instruction も渡せます。

```claude
/compact preserve the test failures and the chosen API design
```

summary は指定したものを残します。これは Claude Code で最も使われていない command の 1 つです。長いタスクの大きな区切りでは実行してください。

### `/clear` : 同じ repo で新しく始める

```claude
/clear
```

会話を消します。CLAUDE.md は引き続き読み込まれます。1 つのタスクを終えて、同じ project で別のタスクを始めるときに使います。Boris Cherny の [advice](https://howborisusesclaudecode.com/) は、積極的に `/clear` することです。次のタスクがかなり軽く感じるはずです。

### `/rewind` "summarize from here" : 部分 compact

これは [5章](#5-resuming-sessions) で見ました。別の knob です。最近の turn はそのまま残し、古い部分だけ要約します。進捗が出た直後で、最後の細部は失いたくないが、初期探索は圧縮していいときに向いています。

### `/btw` : ついでの質問

```claude
/btw what's the difference between Sonnet and Opus?
```

`/btw` は dismissible overlay を開きます。質問と Claude の回答は conversation history に入りません。今知りたいけれど、あとで session を汚したくない話に使います。

btw

### 終了して新しく始める

最後の手段です。Claude Code を終了し（`Ctrl+C` twice または `/exit`）、新しいセッションを始めます。前のセッションが stuck、confused、あるいは同じ点を 3 回直したときに使います。

### 目安

**1 session, 1 goal.** Bug fix と refactor と doc rewrite は 3 つの session であって、1 つではありません。Claude Code の creator である Boris は、逆のやり方を "kitchen sink session" と呼んでいます。全部が 1 つの会話に放り込まれ、context が膨れ、quality が落ちます。`/clear` は無料です。

CLAUDE.md で compact の仕方を伝えることもできます。

```markdown
## On compaction

When compacting, always preserve:
- the chosen API contract
- any test failures we've seen
- any decisions we explicitly made
```

context limit に近づくと auto-compaction が走りますが、先に `/compact` するほうが安く、結果もタスクに合いやすいです。

---



## 7. Skills: 探す、入れる、使う

Skill は `/skill-name` で呼び出せる、まとまった instruction set です。必要なら tool restrictions も付けられます。ざっくり言うと、「Claude に X をやってほしいときの自分流」を 1 つの slash command にしておく仕組みです。

### `/skills`

セッション内で次を打ちます。

```claude
/skills
```

skills

現在読み込まれているものが見えます。user-level（`~/.claude/skills/`）と project-level（`./.claude/skills/`）の両方です。

入れたばかりの状態では何もありません。いくつか入れてみます。

### `/plugin` と marketplace

```claude
/plugin
```

plugins

plugin は 1 つ以上の skills（必要なら hooks や MCP servers も）を 1 つにまとめた installable unit です。まずは公式 Anthropic marketplace の `claude-plugins-official` から始めるのがいいです。

まだ入っていなければ:

1. `/plugin` → **Tab to "Marketplace"** → **Add marketplace**。
2. marketplace GitHub repository identifier として `anthropics/claude-plugins-official` を貼る。
3. Confirm。

plugins-marketplace

これで browse できます。便利な starter pack を入れます。plugin は user level か project level に install できます。どの project でも使えるように、だいたい user level に入れています。


| Skill             | What it does                                    |
| ----------------- | ----------------------------------------------- |
| `frontend-design` | 高品質な frontend interface を作る。                    |
| `skill-creator`   | 新しい skill を一緒に作る、または既存の skill を改善する。meta-skill。 |


これらが install されたかは、`/plugin` 内の **Installed** tab で確認できます。

installed-plugins

### Skills を呼び出す

呼び出し方は 2 つあり、どちらも動きます。

**Leading.** prompt の先頭に skill を置く:

```claude
/frontend-design look at @src/cute/blackwell_helpers.py and design a modern and clean HTML UI for me to visualize this code intuitively.
```

**Mid-prompt.** より大きな instruction の中に skill を埋め込む:

```claude
fix the failing test in @examples/inference/test_blackwell_helpers.py, then /code-simplifier the result.
```

Mid-prompt invocation が動くのは、skills が Claude の呼べる tools として mounted されているからです。別 command を実行しているのではなく、その tool を使うよう促しています。

### デモを 3 つ

**Demo 1: 複雑な codebase に `/frontend-design` を使う。**

[src/cute/flash_fwd.py](https://github.com/Dao-AILab/flash-attention/blob/main/flash_attn/cute/flash_fwd.py) の code を可視化したいとします。複雑になってきていて、追いづらいからです。

```claude
/frontend-design look at @src/cute/flash_fwd.py and design a modern and clean HTML UI for me to visualize this code intuitively.
```

frontend-design-skill

Opus 4.7 with xhigh effort と `frontend-design` skill で、たった 1 つの prompt から生成されたものがこれです。

frontend-design-result

初回としては悪くないと思います。かなり interactive でもあり、ここから学べそうです。

**Demo 2: UI をさらに改善するために `/frontend-design` を使う。**

さらに UI を改善したいとします。もう一度 `frontend-design` skill で頼めます。

```claude
please help me improve this ui further for this file. pasting the screenshot here to show you how it looks: [Image #1]. this is genuinely good, but the text could be a bit more legible, perhaps? continue to use the /frontend-design skill
```

frontend-design-2nd-prompt

結果はこうです。

frontend-design-2nd-result

残念ながら、これはまだ最初の prompt の結果とかなり似ています。どんな変更をしたいのか、もう少し具体的に書くべきでした。このまま続けて、さらに改善していくこともできます。

---



## 8. 自分の Skills を作る

Skills が「便利」から「workflow の中核」になる理由は、作るのがとても簡単だからです。Skill は `**SKILL.md` ファイルを持つ directory** です。それだけです。

### SKILL.md の構造

```markdown
---
name: commit
description: Commit current work with a properly formatted message. Triggers on "commit", "save", "checkpoint".
allowed-tools: Read, Grep, Bash
disable-model-invocation: false
---

# Commit

[the body - whatever instructions Claude should follow when this skill is invoked]
```

Frontmatter fields:


| Field                      | What it does                                                                         |
| -------------------------- | ------------------------------------------------------------------------------------ |
| `name`                     | Slash-command name。`/commit`。directory name と一致する必要があります。                            |
| `description`              | One-line summary。`/skills` に表示されます。Claude も、この skill を autonomously に呼ぶか判断するために使います。 |
| `allowed-tools`            | Optional。skill が使える tools を制限します。読むだけで書かない skill に便利です。                              |
| `disable-model-invocation` | `true` の場合、Claude はこの skill を自分で呼びません。`/name` で明示したときだけ発火します。                        |


### Skills の置き場所

2 つあります。

- **User-level.** `~/.claude/skills/<name>/SKILL.md` - すべての project で使えます。
- **Project-level.** `<repo>/.claude/skills/<name>/SKILL.md` - その repo だけで使い、git で共有します。

個人の workflow には user-level を選びます。repository conventions に依存するものは project-level を選びます。

### 3 つの live build

[skills + hooks kit](https://github.com/sumitdotml) を clone することもできますが、最初はいくつか自分で書くと理解しやすいです。

#### `first-skill-commit`（user-level）

[sumit/skills](https://github.com/sumitdotml/skills/blob/main/skills/commit/SKILL.md) から移植したものです。規約は lowercase、past tense、80 chars 未満。

```bash
mkdir -p ~/.claude/skills/first-skill-commit
touch ~/.claude/skills/first-skill-commit/SKILL.md
```

作成した `SKILL.md` に次を貼ります。

```markdown
---
name: first-skill-commit
description: Commit current work with properly formatted messages. Use when the user asks to commit, save progress, or checkpoint their work.
---

Commit current work to git with properly formatted messages.

## Commit Message Format

- First letter lowercase
- First word past tense ("added", "updated", "fixed", "removed")
- Proper nouns/acronyms capitalized as needed
- < 80 chars single line, unless explicitly asked for multi-line

Examples:
- `added dataset verification script`
- `fixed gradient flow in MoE router`
- `updated readme with setup instructions`

## Instructions

1. Run `GIT_EDITOR=true git status` to see what changed
2. Run `GIT_EDITOR=true git diff <file>` for each modified file
3. Group related changes into logical commits
4. Stage only related files - don't use `git add -A`
5. After committing, if not on main, ask if user wants to push

## Important

- Prepend `GIT_EDITOR=true` to git commands to avoid blocking
- Only commit when instructed - don't auto-commit subsequent work
- Avoid verbosity - keep messages concise
```

これで、どの repo でも `/first-skill-commit` を実行すれば、毎回 rules を説明しなくても、きちんと format された commit を作れます。

#### `second-skill-coding-principles`（これは behavioral skill なので、ひとまず user-level に置きます）

Behavioral skills は tools を呼びませんが、Claude がどう code するかを形づくります。同じ形で、中身だけ違います。`~/.claude/skills/second-skill-coding-principles/` directory に `SKILL.md` を作ります。

```bash
mkdir -p ~/.claude/skills/second-skill-coding-principles
touch ~/.claude/skills/second-skill-coding-principles/SKILL.md
```

そして、作成した `SKILL.md` に次を貼ります。

```markdown
---
name: second-skill-coding-principles
description: Behavioral guidelines to reduce common LLM coding mistakes. Load this when writing or modifying code to avoid overengineering and unnecessary changes.
user-invocable: true
---

# Coding Principles

## 1. Think Before Coding
State assumptions explicitly. If uncertain, ask. If multiple interpretations exist, present them.

## 2. Simplicity First
Minimum code that solves the problem. No abstractions for single-use code. No "flexibility" that wasn't requested.

## 3. Surgical Changes
Touch only what you must. Don't refactor unrelated code. Match existing style.

## 4. Goal-Driven Execution
Define success criteria. Loop until verified. "Fix the bug" → "Write a failing test, then make it pass".

## 5. Minimal Comments
Code should be self-documenting. Comments explain why, not what.

## 6. Avoid AI Slop
Before committing, scan your diff for type-casts-to-any, defensive fallbacks, redundant comments. Remove them.
```

これで、どの repo でも `/second-skill-coding-principles` を実行して、より望ましい書き方で code してもらえます。

> この 2 つの skills はデモ用なので、不要になったらいつでも削除できます。directory ごと消しても大丈夫です。

### meta-skill: `/skill-creator`

[7章](#7-skills-discovering-installing-using) で `claude-plugins-official` を install していれば、`/skill-creator` があります。新しい skill を interactive に作るのを手伝ってくれます。何をする skill か、どの tools が必要かを聞き、SKILL.md を draft し、配置します。形を理解するために一度使う価値があります。

> この 6 か月での workflow 改善の大半は、「prompt で同じことを繰り返していると気づく → skill を書く」でした。レバレッジは複利で効きます。

[sumit/skills](https://github.com/sumitdotml/skills) の kit には、ここで見せた skills に加え、いくつかの追加 skills（`writing-style`, `mistake-memory-guardrails`, `model-debate`, `screenshot-naming`, `daily-shutdown`）が入っています。clone して `./install.sh` を実行すれば starter set になります。

> これを入れると、適切な guardrails といくつかの hooks を含む `CLAUDE.md` も install されます。`AGENTS.md` と `.agents` directory が追加されることにも気づくかもしれませんが、これは `.claude` と `CLAUDE.md` と同じ内容です（同じ files への symbolic links です）。`.claude` を変えれば `.agents` も変わり、その逆も同じです。あまり気にする必要はありません。これは主に、自分が Codex と、ときどき OpenCode も使うため、すべてで同じ `.claude` と `CLAUDE.md` を使えるようにするためです。

---



## 9. ガードレール: hooks

**hook** は、Claude Code harness が特定の lifecycle event で実行する script です。prompt や CLAUDE.md にどれだけ「これをするな」と書いても、model はたまにやります。しかし hooks は model の実際の動きより 1 層上にあり、events に基づいて発火する scripts なのでかなり deterministic です。最も useful な event は `PreToolUse` です。Claude が tool call を実行する前に、call を JSON として stdin に渡して実行します。hook が exit code `2` で終了すると、その tool call はブロックされます。

### Lifecycle events

よく使うのは次です。


| Event                         | When it fires                | Common use                                          |
| ----------------------------- | ---------------------------- | --------------------------------------------------- |
| `PreToolUse`                  | すべての tool call の前。           | 危険な commands をブロックし、path restrictions を enforce する。 |
| `PostToolUse`                 | すべての tool call の後。           | Auto-format, log, lint。                             |
| `UserPromptSubmit`            | user が prompt を submit したとき。 | Context injection, prompt rewrite。                  |
| `SessionStart` / `SessionEnd` | Session boundaries。          | Logging, telemetry。                                 |
| `Stop` / `StopFailure`        | turn が終わったとき。                | Status reporting, notifications。                    |


### settings.json

Hooks は `.claude/settings.json`（project）または `~/.claude/settings.json`（user）に置きます。形はだいたいこうです。

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/block-dangerous-git.sh" }
        ]
      }
    ]
  }
}
```

`matcher` は hook がどの tools で発火するかを決めます。`Bash`, `Edit`, `Write`、または `Edit|Write|MultiEdit` のような pipe-separated list です。

### 2 つの hook walkthrough

#### `block-dangerous-git.sh`（PreToolUse, Bash）

script 全体は次です。ただし [skills + hooks kit](#the-meta-skill-skill-creator) を install している場合、`.claude/hooks/` directory にすでに `block-dangerous-git.sh` があります。

```bash
#!/bin/bash
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command')

DANGEROUS_PATTERNS=(
  "git push"
  "git reset --hard"
  "git clean -fd"
  "git clean -f"
  "git branch -D"
  "git checkout \."
  "git restore \."
  "push --force"
  "reset --hard"
)

for pattern in "${DANGEROUS_PATTERNS[@]}"; do
  if echo "$COMMAND" | grep -qE "$pattern"; then
    echo "BLOCKED: '$COMMAND' matches dangerous pattern '$pattern'. The user has prevented you from doing this." >&2
    exit 2
  fi
done

exit 0
```

hook-blocking-git-push

pattern はこうです。stdin の JSON を読み、command を取り出し、list に対して match し、`2` で exit してブロックします。error message は stderr に出て Claude に見えるので、なぜ blocked されたかを理解し、動きを変えられます。

#### `block-pip.sh`（PreToolUse, Bash）

同じ形で、より narrow scope です。例として、`uv` を使っていて pip を一切使わせたくない場合です。

```bash
#!/bin/bash
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command')

if echo "$COMMAND" | grep -qE '(^|;|&&|\|\||\|)\s*pip[0-9]?\s' || echo "$COMMAND" | grep -qE 'python[0-9.]* -m pip\s'; then
  echo "BLOCKED: pip is not allowed. Use 'uv' instead (e.g. 'uv add', 'uv sync', 'uv run'). No venv activation needed." >&2
  exit 2
fi

exit 0
```

ここでは block message が Claude に「代わりに何をすればいいか」も伝えています。redirect 付きの soft-block は、ただの hard wall よりずっと useful です。

### `permissions.deny` で sensitive reads をブロックする

Hooks だけが guardrail ではなく、いちばん簡単なものですらありません。最小 effort で入れられるのは、`settings.json` の `permissions.deny` block です。script も `jq` も不要で、数行の JSON だけで済むことがあります。

```json
{
  "permissions": {
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)"
    ]
  }
}
```

これは Claude Code harness に、この paths を絶対に読ませないよう伝えます。Claude が丁寧に振る舞う必要すらありません。harness が model に contents を見せる前に拒否します。好みに合わせて list を広げてください。以下は自分の personal list です。

```json
"deny": [
  "Read(./.env)",
  "Read(./.env.*)",
  "Read(./secrets/**)",
  "Read(./id_rsa)",
  "Read(~/.aws/credentials)",
  "Read(~/.ssh/**)",
  "Read(./config/*.production.yml)"
]
```

自分はこれを user level の `~/.claude/settings.json` に入れています。ファイルは [here](https://raw.githubusercontent.com/sumitdotml/dotfiles/refs/heads/main/cc/settings.json) にあります。

特定 project で block したい paths があるなら、project-level の `settings.json` にも追加できます。

`Read(...)` matcher は標準の permission-rule syntax を使うので、globs が動き、absolute、home-relative、project-relative paths を指定できます。

他の settings と同様に、deny rules はどちらの scope にも置けます。

- `.claude/settings.json`: project-level。git に commit します。repo-specific secrets paths にはこれが向いています。collaborators も同じ protection を得ます。
- `~/.claude/settings.json`: user-level。どこでも適用されます。`~/.aws/credentials` や `~/.ssh/` のように、どの session にも絶対読ませたくないものに向いています。

rules が読み込まれているかは、セッション内で `/permissions` を実行し、deny list までスクロールすれば確認できます。

### まとめると

2 つの hooks（それぞれ 30 行程度）と、いくつかの `permissions.deny` rules だけで、意味のある safety floor が得られます。

- 破壊的な git operations: blocked。
- Pip usage: blocked。`uv` への redirect 付き。
- Secrets と dotfiles: unreadable。

これは `--dangerously-skip-permissions` を雑に実行する免許ではありません。この flag は hooks があっても危険です。次の章では sandboxes（より強い OS-level guarantee）と、bypass flag をいつ使ってよいのかという正直な話に入ります。

---



## 10. Sandboxes

`/sandbox` は Claude Code の OS-level isolation です。2025年11月に research preview として出て、現在は generally available です。一文で言うと、Bash commands が何を読み、何を書き、どこへ network 接続できるかに壁を作ります。公式 docs は [docs.claude.com/en/docs/claude-code/sandboxing](https://docs.claude.com/en/docs/claude-code/sandboxing) にあり、本格的に使うなら読む価値があります。

最初に正直に言うと、以前の draft ではこれを少し過大評価していました。sandbox は `**--dangerously-skip-permissions` を付けて放置していい免許ではありません**。これは 1 つのもの（Bash）に対する強い isolation layer であり、そのように扱うべきです。

### 実際に隔離するもの

2 つの layer があります。

- **Filesystem.** デフォルトでは、Bash subprocesses は current working directory とその subdirs の中だけを read/write できます。project 外の任意 path の read は blocked されます。`sandbox.filesystem.allowWrite` / `allowRead` で選択的に広げ、`denyRead` / `denyWrite` で締められます。Enforcement は OS level（macOS は Seatbelt、Linux は bubblewrap）なので、`kubectl`, `terraform`, `npm install`, test runner など、すべての subprocess に効きます。
- **Network.** sandbox 内からの network calls は proxy を通り、pre-approved domains だけを許可します。新しい domain への request は permission prompt を出すか、`settings.json` で `allowManagedDomainsOnly: true` にしていれば silently denied されます。

Sandbox しないもの:

- `Edit`, `Write`, `Read`, `WebFetch`, MCP tools。これらは Claude Code の通常の permission flow（および [9章](#9-guardrails-hooks) の `permissions.deny` rules）を通ります。
- TLS-inspected traffic。proxy は hostname で gate します。TLS を terminate しません。理論上、creative attacker code は allowed domain を通じて tunnel できます。

つまり、`/sandbox` は Bash subprocesses の周りに強い壁を作ります。ほかの guardrails の代わりにはなりません。

### Modes

2 つの mode があります。`/sandbox` で toggle するか、`settings.json` の `sandbox.mode` で設定します。


| Mode                    | What happens                                                                                                                                                                                    |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Auto-allow**          | Sandboxed Bash commands は permission prompts なしで走ります。sandbox restriction に当たった commands は通常の permission flow に fallback します。`/`, `~`, その他 critical paths を target する commands は引き続き prompt します。 |
| **Regular permissions** | Bash commands は通常どおり prompt します。sandbox は permission flow の下に layer されます。摩擦は増えますが、control も増えます。                                                                                                |


多くの人が欲しいのは Auto-allow です。real safety boundary を保ちながら「prompt なし」に最も近づけます。

### Config

同じ `settings.json` ファイルに、新しい top-level block を置きます。

```json
{
  "sandbox": {
    "enabled": true,
    "mode": "auto-allow",
    "filesystem": {
      "allowWrite": ["~/.npm", "/tmp/build"],
      "denyRead":  ["~/.ssh", "~/.aws"]
    },
    "network": {
      "allowedDomains": ["github.com", "registry.npmjs.org", "pypi.org"]
    },
    "excludedCommands": ["docker", "watchman"],
    "allowUnsandboxedCommands": true
  }
}
```

docs から知っておく価値がある points は次です。

- `excludedCommands` は sandbox 下では本当に動かない tools の escape hatch です。Docker、Jest の `watchman`、WSL2 から Windows binaries を起動するものなどです。
- strict にするなら `allowUnsandboxedCommands: false` を設定します。Claude は `dangerouslyDisableSandbox` Bash parameter で一回限りの bypass を request できなくなります。
- Settings arrays は scopes（user → project → local）をまたいで merge されるので、allowlists を project level で拡張できます。

### Platform support

- **macOS**: out of the box。Seatbelt（`sandbox-exec`）を使います。
- **Linux**: `bubblewrap` と `socat` が必要です。Debian/Ubuntu なら `sudo apt-get install bubblewrap socat`。
- **WSL2**: Linux と同じ。bubblewrap を使います。
- **WSL1**: unsupported（kernel namespaces がない）。
- **Windows native**: planned。v2.1.145 時点では未提供。
- **Docker on Ubuntu 24.04+**: `bwrap` user namespaces を許可する AppArmor profile が必要です。

### `--dangerously-skip-permissions` について

ここは慎重に書きたいです。この記事の earlier framing（そして online の多くの guides）は楽観的すぎます。

よく設定された sandbox と `--dangerously-skip-permissions` の組み合わせは、単体の `--dangerously-skip-permissions` よりは *less catastrophic* です。これが正直な表現です。これは「safe」と同じではありません。Anthropic の [engineering post on sandboxing](https://www.anthropic.com/engineering/claude-code-sandboxing) でも、effective isolation には filesystem と network restrictions の両方が必要であり、広すぎる allowlists（例: git のために `github.com` を許可する）が domain fronting による exfiltration paths を開き直す、と明記されています。実際に推奨されているより安全な進化は [auto mode](#4-the-inner-loop-permissions-and-modes) です。sandbox の裏で bypass-permissions するのではなく、classifier が Bash と MCP calls を賢く gate します。

なので、`--dangerously-skip-permissions` を気軽に実行しないでください。本当に使うなら:

- `/sandbox` を有効にし、network allowlist をその task に必要なものだけに絞る。
- 失ってもいい machine、container、VM で実行する。
- **keyboard の前にいる。** Claude が何をしているか見る。すぐ `Ctrl+C` か session quit できる状態でいる。Claude Code instances は本当に変なことをすることがあります。この [December 2025 reddit post](https://www.reddit.com/r/ClaudeAI/comments/1pgxckk/claude_cli_deleted_my_entire_home_directory_wiped/) では、Claude Code が `~/` から `rm -rf` を実行し、filesystem を破壊した例が見られます。sandbox があれば blast radius は working directory でした。なければ machine を壊します。

短く言うと、`/sandbox` は floor を上げますが、`--dangerously-skip-permissions` は ceiling を下げます。組み合わせは *less dangerous* であって、*safe* ではありません。多くの人にとっては Auto mode（[4章](#4-the-inner-loop-permissions-and-modes)）のほうが良い default です（Pro plan users がまだ使えないのは少し残念ですが...）。

### Worktrees: 軽量な代替

sandbox setup なしに parallel work の isolation が欲しいなら、git worktrees は今でもいちばん手軽な道具です。各 worktree は同じ repo から分かれた別 working directory で、独自の `.claude/`、独自の session、独自の permissions を持ちます。

```bash
git worktree add ../myrepo-experiment feature-branch
cd ../myrepo-experiment
claude
```

2 worktrees + 2 `claude` sessions = 2 trains of thought。つまり cross-contamination がありません。軽く、安く、可逆的（`git worktree remove`）に作業を隔離できます。

いくつかの projects で worktrees を試しましたが、思ったようには使いこなせませんでした。ただ、価値を見出す人はいると思います。

---



## 11. 本当にエージェント的に使う: 高度な機能

### Subagents

**subagent** は、独自の context window、独自の system prompt、そして通常は制限された tool set を持つ Claude instance です。main session は focused task のために subagent を spawn できます。subagent は完了まで走り、summary を返し、main context を汚さずに消えます。

すべての install には 3 つの built-in agents が入っています。


| Agent             | What it's for                                                                |
| ----------------- | ---------------------------------------------------------------------------- |
| `Explore`         | 速い read-only search。files を探す、symbols を grep する、「X はどこで定義されているか」に答える。        |
| `Plan`            | 非自明な tasks の implementation plan を作る。step-by-step plan と critical files を返す。 |
| `general-purpose` | catch-all。multi-step research、complex queries。                               |


Claude Code 内の `Agent` tool から呼ぶか、設定されている場合は slash commands から呼びます。独立して走るので、複数を parallel に走らせられます。

**custom subagents** も定義できます。`.claude/agents/<name>.md` に file を置きます。

```markdown
---
name: security-reviewer
description: Reviews code changes for security vulnerabilities.
tools: Read, Grep, Glob, Bash
model: opus
---

You are a security engineer. Review code changes for:
- Authentication and authorization flaws
- Injection vectors (SQL, command, XSS)
- Secrets in code or configs
- Insecure crypto usage

Output: a short list of findings, each with severity (high/medium/low),
file:line reference, and a one-sentence fix suggestion.
```

これで Claude は PR review のために `security-reviewer` を spawn できます。Subagents は Claude Code で最も過小評価されている lever です。主な理由は、誰も custom ones を定義しないからです。2 つか 3 つ、自分用に定義しておくといいです。

### Agent teams

coordinator agent が複数の subagents に delegate し、結果を merge する形です。「lead engineer が sub-tasks を割り当てる」ようなものですが、coordinator も Claude session、subordinates も Claude です。parallelizable work に向いています。たとえば code review で security、performance、style の passes が必要なときです。

### Routines (`/schedule`)

`/schedule` は cron-like routine を作ります。これは local machine ではなく Anthropic の infrastructure 上で動きます。terminal close、machine restart などをまたいでも生き残ります。例:

- 平日 9am に stale PRs を確認し、Slack reminder を投稿する。
- 毎週月曜に先週の commits を要約する。
- deploy 中は毎時 health endpoint を確認し、regression があれば alert する。

Routines は [claude.ai/code](https://claude.ai/code) で見られます。web UI から pause、edit、delete できます。

自分は研究 project でいくつか routines を使いました。毎朝、その cron job が見つけた新しい research directions を Slack app 経由で受け取り、通勤中にすばやく研究状況を確認して、必要なら action を取れるようにしていました。この機能はかなり好きです。

### `/loop`

`/schedule` が「cancel するまで、今後 X minutes/days ごとに」なのに対し、`/loop` は「この session 内で、task が終わるまで X minutes ごとに」です。例:

```claude
/loop 5m check if the deploy completed; if yes, run the smoke tests; if no, wait
```

2 つの modes があります。

- **Fixed interval.** `/loop 5m <prompt>` - 5 分ごとに繰り返す。
- **Dynamic / self-paced.** `/loop <prompt>`（interval なし）- 何を見ているかに基づき、Claude が次にいつ fire するか決める。

最適な use case は、長時間走る external process の babysitting です。CI runs、deploys、大きな migrations などです。自分は 2 日間の GPU training job を研究 project で走らせたときに使いました。とても便利でした。

### `/goal`

これは [v2.1.139](https://github.com/anthropics/claude-code/releases/tag/v2.1.139)（2026年5月）で入りました。「完了するまで作業し続ける」primitive です。例:

```claude
/goal npm test exits 0 and there are no TypeScript errors
```

仕組み:

- condition を述べます。measurable であるべきです。「exits 0」「all 12 tests pass」「homepage renders without errors」など。
- Claude が作業します。各 turn 後、小さな verifier model が conversation transcript に対して condition を確認します。
- condition が満たされていなければ、Claude は自動で続けます。再 prompt は不要です。
- live overlay が elapsed time、turn count、tokens を表示します。
- `/goal pause`, `/goal resume`, `/goal clear` で control します。

避けるべき trap は、**曖昧な goals は永遠に走る**ことです。「これを良くして」は goal ではありません。verifiable な end state がありません。「All 12 unit tests pass」は goal です。`/goal` と [9章の hooks](#9-guardrails-hooks) を組み合わせると、勝手に wander off しない autonomous worker になります。無限に token budget があり、大きな codebase migration や huge refactor を複数 steps で進めたい人にはかなり useful です。これと `/plan` mode の組み合わせは非常に強力です。

### `/batch`

Fan-out です。同じ prompt を複数 inputs（files, branches, list items）に対して走らせます。

```claude
/batch on each file under src/api/handlers/, add JSDoc to exported functions
```

各 input は separate context で処理されるので、互いに干渉しません。「X 全部にこの変更を適用する」task に便利です。各処理が終わると報告します。

### Background tasks

Claude が長時間の shell command を走らせるとき、background task として flag できます。Claude はそれが終わると *notified* されます。polling も `sleep` loops も不要です。待っている間に別の作業を頼むことも、複数の background tasks を同時に走らせることもできます。

仕組みは `Bash` tool の `run_in_background` flag に組み込まれています。特別なことは不要です。「run this in the background」「kick off the deploy, then keep working on X」と言えば、Claude が bookkeeping をします。

### Headless mode (`claude -p`)

`claude -p "..."` は one-shot prompt を実行して終了します。`--output-format json` や `stream-json` と組み合わせると、Claude を pipeline に組み込めます。

```bash
for file in $(git diff --name-only main...HEAD); do
  claude -p "review $file for security issues" \
    --output-format json \
    --allowedTools "Read,Grep" \
    >> review.jsonl
done
```

これは fan-out pattern の裏側にある形です。よく使う pattern は 2 つあります。

- **CI auto-reviewers.** すべての PR に `claude -p` step を入れる。
- **Bulk transforms.** 「`schemas/` のすべての JSON schema に type definitions を生成する」。

### Parallel sessions

Git worktrees + multiple `claude` instances:

```bash
git worktree add ../api-refactor   feature/api-refactor
git worktree add ../db-migration   feature/db-migration

# terminal 1
cd ../api-refactor && claude

# terminal 2
cd ../db-migration && claude
```

2 sessions、2 branches、必要なら 2 つの `CLAUDE.md`。sessions は互いを見ません。Boris Cherny はこの pattern について長く話しています。Claude Code team が Claude Code に取り組むときのやり方です。

### Writer / Reviewer

[best-practices doc](https://docs.claude.com/en/docs/claude-code/best-practices) にある two-pass pattern です。

1. **Session A (writer).** feature を実装する。
2. **Session B (reviewer).** *fresh* session を開き、diff を指して review を頼む。

reviewer は writer の rationalizations を context に持っていないので、writer が見逃したものを flag できます。粗いですが効きます。reviewer は subagent でも、完全に別の `claude --resume` instance でも構いません。

自分はこれにかなり近い `model-debate` skill を作っています（[here](https://github.com/sumitdotml/skills/blob/main/skills/model-debate/SKILL.md) にあります）。2 つの models が consensus に達するまで debate し、plan についてかなり強い agreement を得ます。この skill は project の planning phase でもよく効きます。

### HTML artifacts as living documents

これは Anthropic の Claude Code leads の 1 人である Thariq Shihipar が blog post で話していた pattern で、とても面白いと思いました。pitch はこうです。

> Claude に markdown spec を作らせる代わりに、interactive HTML document を作らせる。Claude は HTML をよく知っているし、artifact はどこでも render でき、charts、dropdowns、code samples、dashboards、walkthroughs を含められる。

元記事を読んでください: ["Using Claude Code: The Unreasonable Effectiveness of HTML"](https://claude.com/blog/using-claude-code-the-unreasonable-effectiveness-of-html)。その後、Thariq の [examples gallery](https://thariqs.github.io/html-effectiveness/) を触ってみてください。interactive spec docs から throwaway debugging UIs まで、20 個の real artifacts があります。

この記事を読んで以来、具体的に使ったもの:

- **Refactor の architecture spec。** Markdown では flat list でしたが、HTML 版は clickable diagram になり、展開すると file-level changes を読めました。
- **Project status dashboard。** Claude が毎朝再生成する 1 つの `status.html`。各 project の open tasks、last commit、current owner を表示します。
- **Throwaway debugging UI。** 800 events の stream を triage する必要がありました。Claude は search box と filters を持つ one-page HTML viewer を作りました。`head -200 events.jsonl | jq` より短時間でした。

一度試してみてください。Claude にこう頼みます。

```claude
generate an interactive HTML file at status.html showing the four sections
of this post as a clickable outline, with each section expandable to show
the bullets underneath. inline css, no external deps.
```

違いを感じると、何度も見るものについては markdown ではなくこれを選ぶようになります。

### [11章](#11-truly-agentic-the-advanced-features) の references

- Boris Cherny on Claude Code patterns: [howborisusesclaudecode.com](https://howborisusesclaudecode.com/)。Boris の ten patterns は、「実際にどう使うか」の最も濃いまとめです。
- The Pragmatic Engineer interview with Boris: [Building Claude Code](https://newsletter.pragmaticengineer.com/p/building-claude-code-with-boris-cherny)。長いですが読む価値があります。
- Thariq Shihipar on HTML artifacts: [the blog post](https://claude.com/blog/using-claude-code-the-unreasonable-effectiveness-of-html), [the examples](https://thariqs.github.io/html-effectiveness/)。
- Anthropic's official best-practices doc: [docs.claude.com/en/docs/claude-code/best-practices](https://docs.claude.com/en/docs/claude-code/best-practices)。

---



## 12. 地味だけど本当に大事な基礎

この section は、初日に誰かから渡してほしかったものです。

### `/usage`

```claude
/usage
```

current session の token usage と weekly total を表示します。たくさん作業したときは確認してください。どの tasks が安く、どれが高いかの直感が地に足つきます。

### `/status`

`/status` は session metadata を表示します。同じ情報は [claude.ai/settings/usage](https://claude.ai/settings/usage) にもあります。

### まず、アカウントの課金方式を確認する

5-hour window や weekly cap の話に入る前に、実際にどの種類のアカウントを使っているのか確認してください。Claude Code の挙動自体は同じでも、裏側の課金方式はかなり違うことがあります。特に Enterprise では重要です。Pro / Max subscription の比較的ゆるやかな利用枠と、custom spend cap が付いた usage-based Enterprise seat の課金感覚は混同しやすいからです。


| If you're using...                                 | What usually matters                                                                                               |
| -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| **Pro / Max subscription**                         | 付属の利用枠。5-hour reset と weekly caps が主に効いてきます。                                                                       |
| **Pro / Max with usage credits enabled**           | 通常の plan limit には当たりますが、usage credits で続けられます。その追加分は subscription とは別に standard API rates で課金されます。                 |
| **Usage-based Enterprise**                         | seat access に加え、使った分が API rates で課金されます。実質的な上限は org credit balance、org spend cap、または individual spend cap かもしれません。 |
| **API key / Console / Bedrock / Vertex / Foundry** | token ごとの pay-as-you-go です。rate limits や budget limits はあり得ますが、Pro / Max-style の message window とは別物です。            |


この違いはかなり大事です。$100 の Enterprise spend cap は、$100/month の Max 5x subscription と同じではありません。前者は使った分だけ減る上限で、後者は subscription に含まれる利用枠です。usage-based Enterprise や API billing では、長い session、大きな context、Opus、subagents、繰り返しの tool calls がそのまま実際の費用になります。

なので、思い込む前に確認します。

- Claude で **Settings → Usage** を開き、利用枠、usage credits、dollar spend cap のどれを見ているのか確認する。
- organization に入っている場合は、Team、seat-based Enterprise、usage-based Enterprise のどれなのか確認する。
- Claude Code で API key を使っている場合は、`/cost` で current session の dollar usage を確認できる。
- Console、Bedrock、Vertex、Foundry の場合は、それぞれの billing dashboard を見る。

### 5-hour rolling window

これは、付属の利用枠がある Pro、Max、Team、seat-based plan を使っている場合に理解しておくべき重要な概念です。公式説明はこうです。

> The 5-hour window starts when you *first* used Claude Code 5 hours ago. Not at a clock time. Not at midnight.

つまり 8am に始めたなら、1pm に cut off されます。休憩して 1:30pm に戻れば、window が reset してまた始まります。早めに reset する方法はありません。待つだけです。

おおよその per-window message budgets:


| Plan    | Per 5-hour window |
| ------- | ----------------- |
| Pro     | ~45 messages      |
| Max 5×  | ~225 messages     |
| Max 20× | ~900 messages     |


Pro の heavy users はこれに当たります。Claude Code が primary tool なら Max 5× がちょうどいい plan です。

### Weekly cap

hard 7-day rolling cap です。claude.ai、IDE plugin、Claude Code で共有されます。usage-based Enterprise や API key の場合、対応する心配はたいてい「weekly cap が reset されるまで待つ」ではなく、「spend cap や prepaid balance がどれだけ残っているか」です。通常の subscription で weekly caps に当たるなら、次の tier の価値を得られていないという計算になるので、upgrade するか、`/clear` をもっと意識的に使う時期です。

### `/model`

```claude
/model
```

現在の 3 models を切り替えます（2026年5月時点では、Claude subscription 内の 3 models は Haiku 4.5、Sonnet 4.6 - normal + 1m、Opus 4.7 です。Claude Code API の models ではありません）。目安:


| Model          | Use for                                                                  |
| -------------- | ------------------------------------------------------------------------ |
| **Haiku 4.5**  | 速くて安いですが、本格的なコーディングには使いません。費用が重要なときに存在を知っておく、くらいの位置づけです。                 |
| **Sonnet 4.6** | 日常作業。default。費用と性能のバランスが良い。planning が得意。                                 |
| **Opus 4.7**   | 難しい reasoning。Architecture。厄介な debugging。慎重な thinking が必要なもの。高いので意図的に使う。 |


Auto-routing もあります。指定しなければ Claude Code が model を選びます。ただし override の方法は知っておく価値があります。たとえば plan mode は Opus で始め、実作業は `/model sonnet` に切り替える、などです。

使った分だけ課金される場合、モデル選びには具体的な値段がつきます。2026年5月時点で、Anthropic の API pricing page では Opus 4.7 が input `$5 / MTok`、output `$25 / MTok`、Sonnet 4.6 が input `$3 / MTok`、output `$15 / MTok`、Haiku 4.5 が input `$1 / MTok`、output `$5 / MTok` です。正確な names と prices は変わるので、`/model`、billing dashboard、Anthropic の pricing page を source of truth として扱ってください。実用上は、reasoning が本当に必要なところだけ Opus を使い、作業がはっきりしたら Sonnet に戻す、という習慣が効きます。

### `/permissions` and `/hooks`

Diagnostic です。`/permissions` は現在 allow/deny されているものを表示します。`/hooks` はどの hooks が接続され、どの events で発火するかを表示します。何かが予想外に blocked または allowed されるときに使います。たいてい忘れていた rule があります。自分の `permissions.deny` list は [here](https://raw.githubusercontent.com/sumitdotml/dotfiles/refs/heads/main/cc/settings.json) にあります。

---



## 13. よくある失敗パターン

[best-practices doc](https://docs.claude.com/en/docs/claude-code/best-practices) と自分の経験から、よくある自爆パターンを挙げます。

### Kitchen-sink sessions

bug fix、feature、doc rewrite を 1 つの session に全部入れることです。context が膨れ、quality が落ち、Claude はどの file を扱っているのか混乱し始めます。対策: unrelated tasks の間では `/clear` します。かなり aggressive に。

### 同じことを 2 回直す

「この task は Sonnet を使って」と一度言った。Claude はなぜか Opus に行った。訂正した。2 turns 後にまた起きた。止めます。context が汚れています。`/clear` し、goal を一度だけ上に書き直して restart します。

Boris Cherny のざっくりした rule は、同じ点で 2 回 correction したら、3 回目は無駄、というものです。session に必要なのは reset であって、もう一押しではありません。

### Over-specified CLAUDE.md

300 行の CLAUDE.md は、instruction problems を instructions で直そうとしているサインです。rule が deterministic なら hook に変換します（[9章](#9-guardrails-hooks)）。「Claude がすでにできること」なら削除します。数週間に一度 CLAUDE.md を trim してください。役に立っていない rules が見つかります。

### Trust without verify

Claude に bug fix を頼んだ。Claude が「fixed!」と言った。そこで終わりにした。6 時間後、test が platform 上で skip されていて、実際には fix が走っていなかったと分かる。**必ず verification を要求します。** `/verify` を使います（[7章](#7-skills-discovering-installing-using)）。test を自分で走らせます。diff を読みます。Trust-but-verify は paranoia ではなく、agentic の代償です。

### Infinite exploration

曖昧な質問をしたら、Claude が 3 層の dependencies を grep しながら 10 分経っている。止めます。plan mode（`Shift+Tab`）に入り written plan を強制するか、exploration を `Explore` subagent に渡して main session を汚さないようにします。

### `--dangerously-skip-permissions` without hooks

典型例です。速さが欲しくて permissions を skip した。Claude が branch の「noise」を片づけるために `git push --force` を走らせた。[9章](#9-guardrails-hooks) が入っていない限り、やらないでください。hooks なしでは shotgun です。hooks があっても footgun ですが、少なくとも多くの場合、反応する時間はあります。

---



## 14. 次に見るもの

ここまでで Claude Code の重要な concepts と features はだいたい covered できました。ほかに見ておくといい resources は次です。

- **Official best practices**: [docs.claude.com/en/docs/claude-code/best-practices](https://docs.claude.com/en/docs/claude-code/best-practices)。必読です。月に一度読み返してください。更新されます。
- **Boris Cherny's patterns**: [howborisusesclaudecode.com](https://howborisusesclaudecode.com/)。10 patterns、全部 useful です。Boris は Anthropic の Claude Code lead なので、これは source に近いです。
- **Thariq Shihipar on HTML**: [the blog post](https://claude.com/blog/using-claude-code-the-unreasonable-effectiveness-of-html) と [the examples](https://thariqs.github.io/html-effectiveness/)。artifact の作り方を最も変えた single pattern です。
- **The Pragmatic Engineer interview with Boris**: [Building Claude Code](https://newsletter.pragmaticengineer.com/p/building-claude-code-with-boris-cherny)。design の behind the scenes を知るために。
- **My skills + hooks kit**: [sumit/skills](https://github.com/sumitdotml/skills)。clone して `./install.sh` を実行すれば starter set になります。
- **Release notes**: [github.com/anthropics/claude-code/releases](https://github.com/anthropics/claude-code/releases)。数週間に一度 skim してください。features は速く ship されます。

今週 3 つだけやるなら:

1. main repo 用の `CLAUDE.md` を書いて commit する。
2. `claude-plugins-official` を install し、`/frontend-design` や `/skill-creator` のような skills を試す。
3. [9章](#9-guardrails-hooks) の 3 つの hooks を `~/.claude/settings.json` に入れる。小さな task で `--dangerously-skip-permissions` を試し、違いを体感する。

typing をやめて delegation を始める準備ができたら、[11章](#11-truly-agentic-the-advanced-features) に戻ってきてください。

---

## 15. Bonus

毎日どれだけ prompt を書いているかに気づくと、typing はかなり遅く感じます。Claude Code には `/voice` mode もあり、Claude に prompt を話して入力できます。詳しくは [here](https://code.claude.com/docs/en/voice-dictation) にあります。