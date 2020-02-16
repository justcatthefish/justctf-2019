#!/usr/bin/env python2
# -*- coding: utf-8 -*-

TEMPLATE = u'''
<style>
pre{
    white-space: pre-wrap;
    word-wrap: break-word;
}
</style>
<pre>
Dear {{_PERSON_}},

How are you and your family today? Hope fine, thank you very much for your response. As I had previously informed you, I contacted you in this transaction for our mutual benefit and for a lasting business relationship with you, having made unsuccessful attempts upon my several enquiries to locate any of my late client’s extended relatives. After these several unsuccessful attempts, I decided to contact you as you have the same last name with him.

Let it be mentioned for the sake of record that this our mutual benefit transaction is absolutely legitimate and all the necessary documents needed in a transaction of this nature will duly and legally be issued and obtained in your name and favor. Please understand that I am an adult with a family and I am only thinking of how to establish the legacy for my children and that is exactly why I am contacting you in this business. Let me go straight to explain more on the event that led to this before I expatiate on the project proper. My Late Client by name  (Engr. {{scam.victim.surname}}), was a big customer of the Bank. He operated a coded account with the Bank before he died on a motor accident on the 31st October, 2014, along with his wife and their only daughter by 4: pm in the evening.

You must understand that in the banking industry opportunities like this are common but not heard. People put their monies in banks or financial institutions and some of these accounts are either coded or confidentially operated. Therefore, when such people die what do you think that happens to these monies when nobody comes for their claims? Well, this is one of the numerous avenues monies are made within and among st the financial institution management or bankers.

In fact, (Engr. {{scam.victim.surname}}), was one of my best clients and I did not mastermind his death and I did not operate or manage his account. I did all I could to locate his real relatives but  was unsuccessful. It was after the unsuccessful attempts to locate his real relatives that I then came to remember his informing me of his early live and experiences. Normally, when something like this happens in banks it is reported to the management. The Management can only wait for some years for the next of kin to show up without publishing it or making it public because of course that false claimants must definitely show up.

Therefore, it is not published and the respective bank only informs the customer’s attorney as the case may be and then only waits for the real heir to show up as the availability of such funds are expected to be in the late "customer's will" which would be the only source of knowledge of it by anybody who is entitled to such fund. if no claimant comes forward then the Bank Management sends the money to the Debt Re-conversion Department and the account is closed. Now the question is, who runs the Debt Re-conversion Department and who is the Management? The answer is simple. The Chairman, Managing Director and Board Members.

These are individuals and these monies are shared by them and nobody asks questions, period. In fact, these issues are not even discussed outside board meetings. To explain myself properly, I am not a board member and of course, I am not part of the Management and I do not work with the Bank. I am not rich, therefore, if I have this opportunity and throw it to the wolves, then I must be the "stupidest" the most "foolish-man" that has ever lived. I have fully put everything in place and since this is an opportunity open to anybody, I do not see anything wrong in what we are doing as long as we are not hurting who should not be hurt period. I can only tell you that it is just destiny that brought us together.

I am quite sure of what I am doing that is why I am committing myself in this project and that is why my life and entire career is involved in this transaction in making it a success. The procedure of establishing the next of kin would be taken care of. For the fact that he has the same last/surname with you, you can with my aid as his personal lawyer be approved by the Bank as his next of kin because I have all the secret information that are contained in this security file jacket with the Bank that will facilitate that. Unfortunately my late client did not have any Will before his sudden death. Although he had earlier notified me of that in the near future.

It is therefore with absolute confidence that I wish to inform you more of the details of this transaction of great mutual benefit. Now be advised my friend, in line with my operational master plan for the success of this our mutual benefit business, what you are required to do now is to tender an application to the Bank as next of kin to this deceased customer putting claim over his balance with the Bank. This application will be written on your name letter headed paper or otherwise, then fax to the Bank for immediate action and processing to start.

As soon as the bank receives the application, documentation for the claim will automatically start. It will be tendered to the Board of Directors of the Bank for approval. As soon as the approval is obtained, you will be issued an approval letter, approving your application as the next of kin/sole beneficiary to Late (Engr. {{scam.victim.surname}}) business starts from there. You will also notify the Bank in your application that you wish your deceased cousin's fund inherited and transferred into your designated account that you will submit at the time of funds transfer.

As soon as the bank management transferred the inheritance fund into your account there in your country, I will then prepare myself and start coming with my Wife to your country for the sharing of the fund and for investment purposes which you will link me in any good business that i will invest some part of my own share of the fund there in your country. For being involved in this transaction of {{scam.victim.money}}, I have therefore resolved to offer you 50% of the total sum as gratification in helping me champion this business. While 50% will be for me.  Please, understand that I put so many things into consideration before offering you this 50% and I do hope that it will be appreciated.

As soon as you give me your hands of co-operation, I will send to you the specimen of the text of application you will send to the Bank and this transaction will commence immediately.  Please as you reply, let me have the following information which I will use to draft the claim application and also for documentations of the probate processes if you make up your mind to co-operate with me for our mutual benefit.


The information are :
 
1. Your full names ......................... ..

2. Date of birth ........................

3. Full contact address .......... (Home or Office)

4. Private telephone numbers .......................

5. Fax numbers ................

6. Marital situation .......................

7. Occupation .................. .......

8. Country .........................

9. Your private email address .........................
 
For further clarifications feel free to call me on my direct number {{scam.scammer.phone_number}}
My regards to you and your family and God bless.
 
{{scam.scammer.full_name}}
</pre>
'''


def generate_scam(person):
    return TEMPLATE.replace('_PERSON_', person)